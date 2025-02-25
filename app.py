# flask_app.py
from flask import Flask, jsonify, render_template
import requests
import mysql.connector
import joblib

app = Flask(__name__)

# Database Configuration (Update with your credentials)
DB_CONFIG = {
    "host": "localhost",
    "user": "your_user",
    "password": "1234",
    "database": "dublin_data"
}

# JCDecaux API Config 
JCDECAUX_API_KEY = "722dc1ade8654c25d8c02e0d0e5f8a303e76131e"
BIKES_API_URL = f"https://api.jcdecaux.com/vls/v1/stations?contract=dublin&apiKey={JCDECAUX_API_KEY}"

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/api/stations', methods=['GET'])
def get_stations():
    response = requests.get(BIKES_API_URL)
    data = response.json()
    return jsonify(data)

@app.route('/api/weather', methods=['GET'])
def get_weather():
    # Placeholder for weather API integration
    return jsonify({"temperature": 12, "humidity": 80, "description": "Cloudy"})

@app.route('/api/predict', methods=['POST'])
def predict_availability():
    model = joblib.load("l") (bike_model.pki)# Placeholder
    # Example prediction input
    prediction = model.predict([[12, 80, 14]])  # Temp, Humidity, Hour
    return jsonify({"predicted_bikes": int(prediction[0])})

if __name__ == '__main__':
    app.run(debug=True)
