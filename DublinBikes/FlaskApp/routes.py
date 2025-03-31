from flask import render_template, jsonify, request, redirect, url_for, session, flash
from DublinBikes.Utils.params import *
from DublinBikes.FlaskApp import app
from DublinBikes.FontEndData.data_loader_csv import (
    read_bike_data_csv,
    read_weather_data_csv,
)
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
from DublinBikes.SQL_code.user_db import (
    register_user,
    get_user_by_email,
    update_user_profile,
)

from datetime import datetime, timedelta


@app.route("/")
def home():

    # Get all the stations first, then after they are all place on the MAP, JS will update the info
    stations = get_all_stations_data_SQL()

    default_station_data = None

    # If the user is logged in and has set a default station, use it;
    # otherwise, fallback to Dame Street (station_id 10)
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


@app.route("/about")
def about():
    return render_template("about.html")


# Display detailed info for a particular station.
@app.route("/station/<int:station_id>")
def station_view(station_id):

    station_list = get_station_data(station_id)
    if not station_list:
        return f"No data found for station {station_id}", 404
    # Assuming get_station_data returns a list, we pick the first record:
    station = station_list[0]

    # Fetch availability records for the current day
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
    data = get_current_weather_data()
    return jsonify(data)


@app.route("/api/forecast_weather")
def forecast_weather_api():

    forecast_type = request.args.get("forecast_type", "current")
    target_datetime = request.args.get("target_datetime")

    if not target_datetime:
        return jsonify({"error": "target_datetime parameter is required"}), 400

    data = get_forecast_weather_data(forecast_type, target_datetime)
    return jsonify(data)


@app.route("/api/current_bikes")
def current_bikes_api():
    data = get_current_bikes_data()
    return jsonify(data)


@app.route("/api/ride_prediction", methods=["POST"])
def ride_prediction():
    # Dummy machine learning model for ride prediction
    import random

    data = request.get_json()
    # Print received data for debugging
    print("Ride prediction request received:")
    print("Timestamp:", data.get("timestamp"))
    print(
        "Weather Conditions - Temperature:",
        data.get("temperature"),
        "Rain:",
        data.get("rain"),
        "Wind Speed:",
        data.get("windspeed"),
    )
    print("Destination Station ID:", data.get("destination_station_id"))
    print("Departure Station ID:", data.get("origin_station_id"))

    # Generate a random prediction value (simulate the ML model output)
    prediction = random.randint(0, 40)

    return jsonify({"prediction": prediction})


@app.route("/register", methods=["GET", "POST"])
def register():

    stations = sorted(get_all_stations_data_SQL(), key=lambda s: s["name"])

    if request.method == "POST":
        email = request.form.get("email")
        username = request.form.get("username")
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        password = request.form.get("password")
        default_station = request.form.get("default_station")

        if register_user(
            email, username, first_name, last_name, password, default_station
        ):
            flash("Successfully registered: Please log in.")
            return redirect(url_for("login"))
        else:
            flash("Error: Email or username already in use.")
    return render_template("register.html", stations=stations)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user = get_user_by_email(email)
        if user and user["password"] == password:
            session["user"] = dict(user)  # Store the user's data in the session
            flash("Successfully logged in.")
            return redirect(url_for("home"))
        else:
            flash("Error: Invalid email or password.")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.pop("user", None)
    flash("Successfully logged out.")

    # Redirect to the previous page, or the home page if there is no referrer.
    return redirect(request.referrer or url_for("home"))


@app.route("/edit_profile", methods=["GET", "POST"])
def edit_profile():
    # Ensure the user is logged in
    if "user" not in session:
        flash("Please log in to edit your profile.")
        return redirect(url_for("login"))

    user = session["user"]

    # Retrieve list of stations for the default_station select input
    stations = sorted(get_all_stations_data_SQL(), key=lambda s: s["name"])

    if request.method == "POST":
        # Get updated profile values from the form
        username = request.form.get("username")
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        password = request.form.get("password")
        default_station = request.form.get("default_station")

        # Call the update function; note: email remains unchanged.
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
            # Update session with new values
            session["user"]["username"] = username
            session["user"]["first_name"] = first_name
            session["user"]["last_name"] = last_name
            session["user"]["password"] = password
            session["user"]["default_station"] = int(default_station)
            return redirect(url_for("home"))  # Redirect to home after successful update

        else:
            flash("Error updating profile. Please try again.")

        return redirect(url_for("edit_profile"))

    return render_template("edit_profile.html", user=user, stations=stations)

