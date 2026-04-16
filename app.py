import os
from flask import Flask, send_from_directory, request, jsonify
import urllib.request
import json
import logging

app = Flask(__name__, static_folder='.', static_url_path='')
logging.basicConfig(level=logging.INFO)

# The user provided Gemini API Key
GEMINI_API_KEY = 'AIzaSyCISvrCPsJPhUEw04iPSAGOeNo3-rm4hGY'

@app.route('/')
def home():
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('.', path)

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '')
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
    
    payload = {
        "contents": [{
            "parts": [{"text": "You are EcoPickup AI, a helpful, eco-friendly assistant that tells users how to correctly segregate waste into wet, dry, recyclable, or e-waste categories. Be concise and friendly. User asks: " + user_message}]
        }]
    }
    
    try:
        req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            reply = result['candidates'][0]['content']['parts'][0]['text']
            return jsonify({'reply': reply})
    except Exception as e:
        app.logger.error("Error communicating with Gemini API: %s", e)
        return jsonify({'reply': f"Sorry, I couldn't connect to my AI database. Error: {str(e)}"}), 500

if __name__ == '__main__':
    print("EcoPickup Web App running on http://127.0.0.1:5000")
    app.run(host='127.0.0.1', port=5000, debug=True)
