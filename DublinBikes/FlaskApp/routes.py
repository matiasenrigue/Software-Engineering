from flask import render_template, jsonify, request, redirect, url_for, session, flash
from DublinBikes.Utils.params import *
from DublinBikes.FlaskApp import app
from DublinBikes.FontEndData.data_loader_csv import read_bike_data_csv, read_weather_data_csv
from DublinBikes.FontEndData.data_loader_SQL import get_station_data, get_all_stations_data, get_one_station_data
from DublinBikes.FontEndData.data_loader_realtime import get_current_data
from DublinBikes.SQL_code.user_db import register_user, get_user_by_email


@app.route('/')
def home():
    weather = read_weather_data_csv()
    stations =  read_bike_data_csv()
    default_station_data = None
    
    # If the user is logged in and has set a default station, use it;
    # otherwise, fallback to Dame Street (station_id 10)
    if 'user' in session and session['user'].get('default_station'):
        default_station_id = session['user'].get('default_station')
    else:
        default_station_id = 10  # Dame Street
        
    default_station_data = get_one_station_data(default_station_id)
    
    print(default_station_data)
    
    return render_template('home.html', 
                           weather=weather, 
                           stations=stations,
                            default_station=default_station_data,
                           mapskey=MAPS_API_KEY)


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






@app.route('/register', methods=['GET', 'POST'])
def register():
    
    stations = sorted(get_all_stations_data(), key=lambda s: s['name'])
    
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        password = request.form.get('password')
        default_station = request.form.get('default_station')
        
        if register_user(email, username, first_name, last_name, password, default_station):
            flash('Successfully registered: Please log in.')
            return redirect(url_for('login'))
        else:
            flash('Error: Email or username already in use.')
    return render_template('register.html', stations=stations)



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = get_user_by_email(email)
        if user and user['password'] == password:
            session['user'] = dict(user) # Store the user's data in the session
            flash('Successfully logged in.')
            return redirect(url_for('home'))
        else:
            flash('Error: Invalid email or password.')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('Successfully logged out.')
    
    # Redirect to the previous page, or the home page if there is no referrer.
    return redirect(request.referrer or url_for('home'))





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