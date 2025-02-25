from flask import render_template, jsonify
from DublinBikes.FlaskApp import app
from DublinBikes.FontEndData.data_loader_csv import read_bike_data_csv, read_weather_data_csv
from DublinBikes.FontEndData.data_loader_SQL import get_station_data
from DublinBikes.FontEndData.data_loader_realtime import get_current_data


@app.route('/')
def home():
    weather = read_weather_data_csv()
    stations = read_bike_data_csv()
    return render_template('home.html', weather=weather, stations=stations)


@app.route('/about')
def about():
    return render_template('about.html')


# Display detailed info for a particular station.
@app.route('/station/<int:station_id>')
def station_view(station_id):
    station = get_station_data(station_id)
    if not station:
        return f"No data found for station {station_id}", 404
    return render_template('station.html', station=station)


# Page that will display current data in JSON format.
@app.route('/currentdata')
def currentdata_page():
    return render_template('currentdata.html')


# API endpoint: Return current data (both bikes and weather) in JSON.
@app.route('/api/current_data')
def current_data_api():
    data = get_current_data()
    return jsonify(data)





###### DELETED CODE

"""
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
"""