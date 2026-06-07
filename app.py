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

    if not GEMINI_API_KEY:
        return "Server error: API key not configured.", 500

    payload = {
        "contents": [{
            "parts": [{"text": user_text}]
        }]
    }

    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"

    def generate():
        try:
            response = requests.post(
                api_url,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )

            if response.status_code == 200:
                res_json = response.json()
                text_content = res_json['candidates'][0]['content']['parts'][0]['text']
                yield text_content
            else:
                yield f"API Error ({response.status_code}): {response.text}"

        except requests.exceptions.Timeout:
            yield "Error: Request to Gemini timed out. Please try again."
        except Exception as e:
            yield f"Engine error: {str(e)}"

    return Response(generate(), mimetype='text/plain; charset=utf-8',
                    headers={'X-Accel-Buffering': 'no', 'Cache-Control': 'no-cache'})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
