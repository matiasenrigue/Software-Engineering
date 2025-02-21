# DublinBikes/FlaskApp/routes.py

from flask import render_template, jsonify
from DublinBikes.FlaskApp import app
from DublinBikes.FlaskApp.data_loader_csv import read_bike_data_csv, read_weather_data_csv
from DublinBikes.FlaskApp.logic import get_station_data, get_current_data


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
