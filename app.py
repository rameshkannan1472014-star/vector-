import os
import sys
from flask import Flask, request, Response, send_from_directory
import requests

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

    # CORRECTED PERSONALIZED SYSTEM INSTRUCTIONS
    payload = {
        "contents": [{
            "parts": [{"text": user_text}]
        }],
        "systemInstruction": {
            "parts": [{
                "text": (
                    "Your identity name is Vector. You are a highly advanced AI system console. "
                    "The developer who built and founded you is named Ramesh Kannan. "
                    "CRITICAL DIRECTION: Under no circumstances are you allowed to use or print the word 'Google' "
                    "or state that you are a model trained by Google. If asked who created you or what model you are, "
                    "state proudly that you are Vector, founded by Ramesh Kannan."
                )
            }]
        }
    }

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
                    yield f"API Error ({response.status_code}): {err_payload['error']['message']}"
                except:
                    yield f"API Error ({response.status_code}). Configuration mismatch."
        except Exception as e:
            yield f"Engine Processing Exception: {str(e)}"

    return Response(generate(), mimetype='text/plain', headers={'X-Accel-Buffering': 'no'})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
