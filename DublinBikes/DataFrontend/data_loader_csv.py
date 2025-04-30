import csv
import ast
import os
from datetime import datetime

"""
Module: data_loader_csv
-----------------------
This module contains functions for reading bike station and weather data from CSV files.
Note: Although these functions are not currently used, they are kept for future reference.
"""


def get_csv_folder_path():
    """
    Get the absolute path to the folder containing the CSV data files.

    Returns:
        str: The absolute path to the CSV data folder.
    """
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")


def read_bike_data_csv():
    """
    Read bike station data from a CSV file.

    This function reads bike station data from 'bikes_24h.csv' and returns a list of station dictionaries.
    It ensures that each station is only added once by using a set of unique station names.

    Returns:
        list: A list of dictionaries, each containing data for a bike station such as name, address, station_id,
              position, bike stands, available bike stands, and available bikes.
    """
    data_path = os.path.join(get_csv_folder_path(), "bikes_24h.csv")
    set_of_unique_stations = set()
    stations = []
    with open(data_path, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            station_name = row.get("name")
            if station_name in set_of_unique_stations:
                continue
            station = {
                "name": station_name,
                "address": row.get("address"),
                "station_id": row.get("number"),
                "position": ast.literal_eval(row.get("position")),
                "bike_stands": row.get("bike_stands"),
                "available_bike_stands": row.get("available_bike_stands"),
                "available_bikes": row.get("available_bikes"),
            }
            stations.append(station)
            set_of_unique_stations.add(station_name)
    return stations


def read_weather_data_csv():
    """
    Read weather data from a CSV file.

    This function reads the first row of the 'weather_24h.csv' file and extracts weather information.
    It parses string representations of Python dictionaries/lists using ast.literal_eval.

    Returns:
        dict: A dictionary containing weather data including temperature, description, sunrise, and sunset.
              Returns an empty dictionary if no data is available.
    """
    data_path = os.path.join(get_csv_folder_path(), "weather_24h.csv")
    with open(data_path, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        row = next(reader, None)
        if row:
            main_data = ast.literal_eval(row.get("main"))
            temperature = main_data.get("temp")
            weather_list = ast.literal_eval(row.get("weather"))
            description = (
                weather_list[0].get("description")
                if weather_list and isinstance(weather_list, list)
                else ""
            )
            sys_data = ast.literal_eval(row.get("sys"))
            sunrise_ts = sys_data.get("sunrise")
            sunset_ts = sys_data.get("sunset")
            sunrise = (
                datetime.fromtimestamp(sunrise_ts).strftime("%I:%M %p")
                if sunrise_ts
                else ""
            )
            sunset = (
                datetime.fromtimestamp(sunset_ts).strftime("%I:%M %p")
                if sunset_ts
                else ""
            )
            return {
                "temperature": temperature,
                "description": description,
                "sunrise": sunrise,
                "sunset": sunset,
            }
    return {}
