import os
import sys
import json
from flask import Flask, request, Response, send_from_directory
import requests

# Force logs to stream cleanly to Render terminal
os.environ["PYTHONUNBUFFERED"] = "1"

app = Flask(__name__, static_folder='.')

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

@app.route('/stream', methods=['POST'])
def handle_stream():
    data = request.get_json() or {}
    user_text = data.get('message', '').strip()
    
    if not user_text:
        return "Message cannot be empty.", 400

    payload = {
        "contents": [{
            "parts": [{"text": user_text}]
        }]
    }

    # Production Model Endpoint Matrix
    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:streamGenerateContent?key={GEMINI_API_KEY}"
    fallback_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:streamGenerateContent?key={GEMINI_API_KEY}"
    
    def generate():
        try:
            # Primary Request Attempt
            response = requests.post(api_url, json=payload, headers={'Content-Type': 'application/json'}, stream=True, timeout=15)
            
            # Fallback Route Handler if 404 is encountered
            if response.status_code == 404:
                response = requests.post(fallback_url, json=payload, headers={'Content-Type': 'application/json'}, stream=True, timeout=15)

            if response.status_code == 200:
                buffer = ""
                for chunk in response.iter_content(chunk_size=512, decode_unicode=True):
                    if chunk:
                        buffer += chunk
                        # Process complete SSE lines out of the stream buffer
                        while "\n" in buffer:
                            line, buffer = buffer.split("\n", 1)
                            line = line.strip()
                            
                            # Standard Google API stream chunks begin with 'data: ' or raw JSON array items
                            if line.startswith("data:"):
                                line = line[5:].strip()
                            
                            if not line or line in ["[", "]", ","]:
                                continue
                                
                            try:
                                chunk_json = json.loads(line)
                                text_content = chunk_json['candidates'][0]['content']['parts'][0]['text']
                                yield text_content
                                sys.stdout.flush()
                            except (ValueError, KeyError, IndexError):
                                # Cleanly bypass structural wrapper arrays
                                pass
            else:
                yield f"Google Production API Error ({response.status_code}). Please verify that your API key is unrestricted in Google AI Studio."
        except Exception as e:
            yield f"Streaming Exception: {str(e)}"

    return Response(generate(), mimetype='text/plain', headers={'X-Accel-Buffering': 'no'})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
