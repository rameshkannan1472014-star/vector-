import os
import sys
from flask import Flask, request, Response, send_from_directory
import requests

# Ensure terminal outputs update immediately in the Render log pipeline
os.environ["PYTHONUNBUFFERED"] = "1"

app = Flask(__name__, static_folder='.')

# Grabs your active credentials from the Render Environment panel
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

    # MATCHES GOOGLE EMAIL: Points exactly to your project's active model string
    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-flash-lite:generateContent?key={GEMINI_API_KEY}"
    
    def generate():
        try:
            response = requests.post(
                api_url, 
                json=payload, 
                headers={'Content-Type': 'application/json'}, 
                timeout=15
            )
            
            if response.status_code == 200:
                res_json = response.json()
                text_content = res_json['candidates'][0]['content']['parts'][0]['text']
                yield text_content
                sys.stdout.flush()
            else:
                try:
                    err_payload = response.json()
                    yield f"Google API Error ({response.status_code}): {err_payload['error']['message']}"
                except:
                    yield f"Google API Error ({response.status_code}). Check your deployment model string matches."
        except Exception as e:
            yield f"Engine Processing Exception: {str(e)}"

    return Response(generate(), mimetype='text/plain', headers={'X-Accel-Buffering': 'no'})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
