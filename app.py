import os
from flask import Flask, request, Response, send_from_directory
import urllib.request
import json

app = Flask(__name__, static_folder='.')

# Fallback key for testing locally inside Pydroid 
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")






@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

@app.route('/stream', methods=['POST'])
def handle_stream():
    data = request.get_json() or {}
    conversation_history = data.get('history', [])
    
    if not conversation_history:
        return "Missing conversation history context.", 400

    system_instruction = (
        "You are VectorAI, a world-class, multi-talented general artificial intelligence. "
        "Your purpose is to assist users with any task imaginable, including complex coding, "
        "creative writing, deep logical analysis, and strategic planning. Be highly intelligent, direct, and helpful."
    )

    contents = []
    for msg in conversation_history:
        role = "user" if msg["role"] == "student" else "model"
        contents.append({"parts": [{"text": msg["text"]}]})

    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-flash-lite:streamGenerateContent?key={GEMINI_API_KEY}"
    
    payload = {
        "contents": contents,
        "systemInstruction": { "parts": [{"text": system_instruction}] }
    }

    def generate_chunks():
        try:
            encoded_data = json.dumps(payload).encode('utf-8')
            req = urllib.request.Request(api_url, data=encoded_data, headers={'Content-Type': 'application/json'})
            
            with urllib.request.urlopen(req, timeout=15) as response:
                for line in response:
                    if not line:
                        continue
                    line_str = line.decode('utf-8').strip()
                    if line_str.startswith(",") or line_str.startswith("[") or line_str.startswith("]"):
                        line_str = line_str.lstrip(",").strip("[]")
                    if not line_str:
                        continue
                    
                    try:
                        chunk_json = json.loads(line_str)
                        text_piece = chunk_json['candidates'][0]['content']['parts'][0]['text']
                        yield text_piece
                    except Exception:
                        pass 
        except Exception as e:
            yield f"\n[Local Error: {str(e)}]"

    return Response(generate_chunks(), mimetype='text/plain')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
    
    