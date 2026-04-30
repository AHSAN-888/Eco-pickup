import os
from flask import Flask, send_from_directory, request, jsonify
import urllib.request
import json
import logging
import pandas as pd
from sklearn.linear_model import LinearRegression

app = Flask(__name__, static_folder='.', static_url_path='')
logging.basicConfig(level=logging.INFO)

# Load or create dataset and train model
dataset_path = 'waste_dataset.csv'
if not os.path.exists(dataset_path):
    data = {
        'household_size': [2, 4, 1, 5, 3, 2, 4, 6, 3, 1],
        'waste_last_week': [5.5, 12.0, 2.0, 15.5, 8.0, 6.0, 10.0, 18.0, 7.5, 3.0],
        'area_code': [1, 2, 1, 3, 2, 3, 1, 2, 1, 3],
        'days_to_pickup': [4, 2, 7, 1, 3, 4, 3, 1, 3, 6]
    }
    pd.DataFrame(data).to_csv(dataset_path, index=False)

df = pd.read_csv(dataset_path)
X = df[['household_size', 'waste_last_week', 'area_code']]
y = df['days_to_pickup']

pickup_model = LinearRegression()
pickup_model.fit(X, y)

logging.basicConfig(level=logging.INFO)

# Read Gemini API key from environment (set in .env or Vercel secrets)
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if GEMINI_API_KEY:
    GEMINI_API_KEY = GEMINI_API_KEY.strip()
else:
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

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"

    payload = {
        "contents": [{
            "parts": [{"text": f"You are EcoPickup AI, a helpful, eco-friendly assistant for the EcoPickup platform in an aesthetic floating chat. EcoPickup connects households with waste collectors for on-demand waste pickup, recycling, and sustainable management. Features include scheduling on-demand pickup, real-time captain tracking, earning points/rewards for waste (especially e-waste and proper segregation), smart segregation guide, and easy onboarding for collection captains (who can earn around $800/week). You can tell users how to sort waste (wet, dry, recyclable, e-waste) and also answer any questions about the EcoPickup website, services, pricing, app features, or how to become a captain. Keep answers concise, super friendly, and formatted nicely. User asks: {user_message}"}]
        }]
    }

    import time
    max_retries = 2
    for attempt in range(max_retries):
        try:
            req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers={'Content-Type': 'application/json', 'User-Agent': 'EcoPickup/1.0'})
            with urllib.request.urlopen(req, timeout=8) as response:
                result = json.loads(response.read().decode('utf-8'))
                reply = result['candidates'][0]['content']['parts'][0]['text']
                return jsonify({'reply': reply})
        except urllib.error.HTTPError as e:
            try:
                error_body = e.read().decode('utf-8')
                error_json = json.loads(error_body)
                error_msg = error_json.get('error', {}).get('message', error_body)
            except:
                error_msg = str(e)
            app.logger.error("Gemini API HTTP Error: %s", error_msg)
            return jsonify({'reply': f"Sorry, I couldn't connect to my AI database. Error: {error_msg}"}), 500
        except Exception as e:
            if attempt < max_retries - 1 and '503' in str(e):
                time.sleep(1)
                continue
            app.logger.error("Error communicating with Gemini API: %s", e)
            return jsonify({'reply': f"Sorry, I couldn't connect to my AI database. Error: {str(e)}"}), 500

@app.route('/api/predict_pickup', methods=['POST'])
def predict_pickup():
    data = request.get_json(silent=True) or {}
    try:
        household_size = float(data.get('household_size', 1))
        waste_last_week = float(data.get('waste_last_week', 0))
        area_code = float(data.get('area_code', 1))
        
        # Predict using the trained model
        prediction = pickup_model.predict([[household_size, waste_last_week, area_code]])
        days = max(1, int(round(prediction[0])))
        
        return jsonify({'message': f"Next pickup should be in {days} days"})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    print("EcoPickup Web App running on http://127.0.0.1:5001")
    host = os.getenv('HOST', '127.0.0.1')
    port = int(os.getenv('PORT', '5001'))
    app.run(host=host, port=port, debug=True)
