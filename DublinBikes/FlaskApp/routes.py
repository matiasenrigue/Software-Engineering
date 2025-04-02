"""
Module: routes
--------------
This module defines the route handlers for the Dublin Bikes Flask web application.
It provides endpoints for rendering web pages, handling API requests, and managing user
authentication and profile editing. The module integrates data from bike station and weather
sources to support interactive features such as real-time bike availability and weather updates.

Dependencies:
    - Utility functions for data retrieval (from FontendData and SqlCode modules).
    - Configuration parameters from the DublinBikes.Utils.params module.
"""

from flask import render_template, jsonify, request, redirect, url_for, session, flash
from DublinBikes.Utils.params import *
from DublinBikes.FlaskApp import app

from DublinBikes.FontEndData.data_loader_SQL import (
    get_station_data,
    get_all_stations_data_SQL,
    get_one_station_data,
    get_station_availability_daily,
)
from DublinBikes.FontEndData.data_realtime_weather import (
    get_forecast_weather_data,
    get_current_weather_data,
)
from DublinBikes.FontEndData.data_realtime_bikes import get_current_bikes_data
from DublinBikes.SqlCode.user_db import (
    register_user,
    get_user_by_email,
    update_user_profile,
)

from datetime import datetime, timedelta
import re
from werkzeug.security import generate_password_hash, check_password_hash


@app.route("/")
def home():
    """
    Render the home page.

    Retrieves all bike station data and determines the default station (based on the
    logged-in user's profile or a fallback value). The home page displays the map with
    station markers and passes the current timestamp for real-time updates.

    Returns:
        str: Rendered HTML for the home page.
    """
    stations = get_all_stations_data_SQL()

    default_station_data = None

    # Use the user's default station if available; otherwise, fallback to Dame Street (station_id 10)
    if "user" in session and session["user"].get("default_station"):
        default_station_id = session["user"].get("default_station")
    else:
        default_station_id = 10  # Dame Street

    default_station_data = get_one_station_data(default_station_id)
    print(default_station_data)

    return render_template(
        "home.html",
        stations=stations,
        default_station=default_station_data,
        mapskey=MAPS_API_KEY,
        now=datetime.now(),
    )



@app.route("/station/<int:station_id>")
def station_view(station_id):
    """
    Render a detailed view for a specific bike station.

    Retrieves station details and the daily availability records for the given station.
    If no data is found, returns a 404 error message.

    Parameters:
        station_id (int): The unique identifier of the bike station.

    Returns:
        str: Rendered HTML for the station details page, or a 404 error message if data is missing.
    """
    station_list = get_station_data(station_id)
    if not station_list:
        return f"No data found for station {station_id}", 404
    station = station_list[0]

    # Fetch daily availability records for the station
    availability_data = get_station_availability_daily(station_id)
    print(availability_data)

    return render_template(
        "station.html",
        station=station,
        availability_data=availability_data,
        mapskey=MAPS_API_KEY,
    )


@app.route("/api/current_weather")
def current_weather_api():
    """
    Provide current weather data as a JSON response.

    Retrieves current weather information using helper functions.

    Returns:
        Response: JSON object containing current weather data.
    """
    data = get_current_weather_data()
    return jsonify(data)


@app.route("/api/forecast_weather")
def forecast_weather_api():
    """
    Provide forecast weather data as a JSON response.

    Expects the following query parameters:
        - forecast_type: Type of forecast (default is 'current').
        - target_datetime: ISO formatted datetime string for which the forecast is requested (required).

    Returns:
        Response: JSON object with forecast weather data, or an error message if parameters are missing.
    """
    forecast_type = request.args.get("forecast_type", "current")
    target_datetime = request.args.get("target_datetime")

    if not target_datetime:
        return jsonify({"error": "target_datetime parameter is required"}), 400

    data = get_forecast_weather_data(forecast_type, target_datetime)
    return jsonify(data)


@app.route("/api/current_bikes")
def current_bikes_api():
    """
    Provide current bike station data as a JSON response.

    Retrieves real-time bike availability information from the cache or the external API.

    Returns:
        Response: JSON object containing current bike data.
    """
    data = get_current_bikes_data()
    return jsonify(data)


@app.route("/api/ride_prediction", methods=["POST"])
def ride_prediction():
    """
    Provide a dummy ride prediction based on input data.

    Simulates a machine learning prediction by generating a random value.
    Logs the received data (timestamp, weather conditions, station IDs) for debugging.

    Returns:
        Response: JSON object with the predicted ride value.
    """
    import random
    from DublinBikes.MachineLearning.predict_availability import prediction

    data = request.get_json()
    
    origin = get_station_data(station_id=data["origin_station_id"])[0]
    destination = get_station_data(station_id=data["destination_station_id"])[0]
    
    result = prediction(data, origin, destination)
  
    return result



# Email regex pattern
EMAIL_REGEX = r"[^@]+@[^@]+\.[^@]+"

@app.route("/register", methods=["GET", "POST"])
def register():
    """
    Handle user registration.

    On GET: Renders the registration form with a list of bike stations.
    On POST: Processes the submitted registration form and attempts to register the user.
            If successful, redirects to the login page; otherwise, flashes an error message.

    Returns:
        str: Rendered HTML for the registration page or a redirection to the login page on success.
    """
    stations = sorted(get_all_stations_data_SQL(), key=lambda s: s["name"])
    if request.method == "POST":
        email = request.form.get("email")
        username = request.form.get("username")
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        password = request.form.get("password")
        default_station = request.form.get("default_station")

        # Validate email format
        if not re.match(EMAIL_REGEX, email):
            flash("Error: Invalid email format.")
            return render_template("register.html", stations=stations)

        # Hash the password before storing it
        hashed_password = generate_password_hash(password)

        if register_user(email, username, first_name, last_name, hashed_password, default_station):
            flash("Successfully registered: Please log in.")
            return redirect(url_for("login"))
        else:
            flash("Error: Email or username already in use.")
    return render_template("register.html", stations=stations)



@app.route("/login", methods=["GET", "POST"])
def login():
    """
    Handle user login.

    On GET: Renders the login form.
    On POST: Validates the submitted login credentials. If valid, stores the user data in the session
            and redirects to the home page; otherwise, flashes an error message.

    Returns:
        str: Rendered HTML for the login page or a redirection to the home page on successful login.
    """
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user = get_user_by_email(email)
        if user and check_password_hash(user["password"], password):
            session["user"] = dict(user)
            return redirect(url_for("home"))
        else:
            flash("Error: Invalid email or password.")
    return render_template("login.html")


@app.route("/logout")
def logout():
    """
    Log the user out by clearing the session.

    After logout, redirects the user to the referring page or to the home page if no referrer exists.

    Returns:
        Response: Redirection to the previous page or home page.
    """
    session.pop("user", None)
    return redirect(request.referrer or url_for("home"))


@app.route("/edit_profile", methods=["GET", "POST"])
def edit_profile():
    """
    Handle user profile editing.

    Ensures the user is logged in before allowing access. On GET, renders the profile edit form
    populated with current user data and bike station options. On POST, updates the user's profile
    and refreshes the session with the new data. Redirects to the home page upon a successful update.

    Returns:
        str: Rendered HTML for the profile editing page or a redirection to the home page on success.
    """
    if "user" not in session:
        flash("Please log in to edit your profile.")
        return redirect(url_for("login"))

    user = session["user"]
    stations = sorted(get_all_stations_data_SQL(), key=lambda s: s["name"])

    if request.method == "POST":
        username = request.form.get("username")
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        password = request.form.get("password")
        default_station = request.form.get("default_station")

        success = update_user_profile(
            user["email"],
            username,
            first_name,
            last_name,
            password,
            int(default_station),
        )

        if success:
            flash("Profile updated successfully.")
            session["user"]["username"] = username
            session["user"]["first_name"] = first_name
            session["user"]["last_name"] = last_name
            session["user"]["password"] = password
            session["user"]["default_station"] = int(default_station)
            return redirect(url_for("home"))
        else:
            flash("Error updating profile. Please try again.")
        return redirect(url_for("edit_profile"))

    return render_template("edit_profile.html", user=user, stations=stations)
