# app.py
from flask import Flask, request, jsonify
import joblib
from utils import clean_text

# Initialize Flask app
app = Flask(__name__)

# Load model and vectorizer
model = joblib.load('svc_model.pkl')
vectorizer = joblib.load('vectorizer.pkl')

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()

    if 'text' not in data:
        return jsonify({'error': 'Missing "text" field'}), 400

    text = data['text']
    cleaned = clean_text(text)
    vector = vectorizer.transform([cleaned])

    # Prediction and confidence
    prediction = model.predict(vector)[0]
    proba = model.predict_proba(vector)[0]
    class_index = model.classes_.tolist().index(prediction)
    confidence = float(proba[class_index])

    return jsonify({
        'input': text,
        'predicted_sentiment': prediction,
        'confidence': round(confidence, 4)
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
