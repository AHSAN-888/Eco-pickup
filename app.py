import os
from flask import Flask, send_from_directory, request, jsonify
import urllib.request
import json
import logging

app = Flask(__name__, static_folder='.', static_url_path='')
logging.basicConfig(level=logging.INFO)

# Read Gemini API key from environment (set in .env or Vercel secrets)
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if not GEMINI_API_KEY:
    logging.error('GEMINI_API_KEY not set in environment')

@app.route('/')
def home():
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('.', path)

@app.route('/api/chat', methods=['POST'])
def chat():
    if not GEMINI_API_KEY:
        return jsonify({'reply': 'Server configuration error: missing Gemini API key.'}), 500
    data = request.get_json(silent=True) or {}
    user_message = data.get('message', '')

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"

    payload = {
        "contents": [{
            "parts": [{"text": f"You are EcoPickup AI, a helpful, eco-friendly assistant for the EcoPickup platform in an aesthetic floating chat. EcoPickup connects households with waste collectors for on-demand waste pickup, recycling, and sustainable management. Features include scheduling on-demand pickup, real-time captain tracking, earning points/rewards for waste (especially e-waste and proper segregation), smart segregation guide, and easy onboarding for collection captains (who can earn around $800/week). You can tell users how to sort waste (wet, dry, recyclable, e-waste) and also answer any questions about the EcoPickup website, services, pricing, app features, or how to become a captain. Keep answers concise, super friendly, and formatted nicely. User asks: {user_message}"}]
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
    host = os.getenv('HOST', '127.0.0.1')
    port = int(os.getenv('PORT', '5000'))
    app.run(host=host, port=port, debug=True)
