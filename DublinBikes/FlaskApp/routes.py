from flask import render_template
from DublinBikes.FlaskApp import app
from DublinBikes.FlaskApp.data_loader_csv import read_bike_data_csv, read_weather_data_csv

@app.route('/')
def home():
    # Load data from CSV files using the auxiliary functions.
    weather = read_weather_data_csv()
    stations = read_bike_data_csv()
    return render_template('home.html', weather=weather, stations=stations)

@app.route('/about')
def about():
    return render_template('about.html')
