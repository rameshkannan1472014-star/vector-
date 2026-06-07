import os
import sys
import json
from flask import Flask, request, Response, send_from_directory
import requests

# Force terminal logs to stream out to Render instantly
os.environ["PYTHONUNBUFFERED"] = "1"

app = Flask(__name__, static_folder='.')

# Securely pull your API key from your Render environment dashboard
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

    # MATCHES YOUR EMAIL: Targets the exact model your key is authorized for
    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-flash-lite:streamGenerateContent?key={GEMINI_API_KEY}"
    
    def generate():
        try:
            response = requests.post(
                api_url, 
                json=payload, 
                headers={'Content-Type': 'application/json'}, 
                stream=True, 
                timeout=15
            )
            
            if response.status_code == 200:
                buffer = ""
                for chunk in response.iter_content(chunk_size=512, decode_unicode=True):
                    if chunk:
                        buffer += chunk
                        while "\n" in buffer:
                            line, buffer = buffer.split("\n", 1)
                            line = line.strip()
                            
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
                                pass
            else:
                yield f"Google Stream Connection Refused ({response.status_code}). Verify your key matches the model."
        except Exception as e:
            yield f"Streaming Exception Interrupted: {str(e)}"

    return Response(generate(), mimetype='text/plain', headers={'X-Accel-Buffering': 'no'})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

