import os
import sys
from flask import Flask, request, Response, send_from_directory
import requests

# Force unbuffered streaming output for Render logs
os.environ["PYTHONUNBUFFERED"] = "1"

app = Flask(__name__, static_folder='.')

# Secure environment variable pickup for your API key
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

    # PRODUCTION FIXED ENDPOINT: Uses the official post-May 2026 GA model string path
    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:streamGenerateContent?key={GEMINI_API_KEY}"
    
    def generate():
        try:
            response = requests.post(api_url, json=payload, headers={'Content-Type': 'application/json'}, stream=True, timeout=15)
            if response.status_code == 200:
                for line in response.iter_lines(chunk_size=1, decode_unicode=True):
                    if line:
                        line_str = line.strip()
                        if '"text":' in line_str:
                            try:
                                start = line_str.find('"text": "') + 9
                                end = line_str.rfind('"')
                                if start > 8 and end > start:
                                    yield line_str[start:end].encode().decode('unicode-escape')
                                    sys.stdout.flush()
                            except:
                                pass
            else:
                yield f"Google Production API Error ({response.status_code}). Check if your API Key is active in AI Studio."
        except Exception as e:
            yield f"Streaming Exception: {str(e)}"

    return Response(generate(), mimetype='text/plain', headers={'X-Accel-Buffering': 'no'})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)


    
    
    