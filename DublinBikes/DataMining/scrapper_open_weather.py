import requests
import traceback
import datetime
import time
import os
import json
import sqlalchemy as sqla

from DublinBikes.Utils.params import WEATHER_KEY, CURRENT_OPENWEATHER_URI
from DublinBikes.SqlCode.sql_utils import execute_sql
from DublinBikes.DataMining.local_scrapping import save_data_to_file

"""
Module: scrapper_open_weather
-----------------------------
This module is responsible for scraping weather data from the OpenWeatherMap API.
It provides functions to fetch current weather data for Dublin and to save that data into the SQL database.
The scraped weather data is used to build a historical database for analysis, training of prediction models,
and for displaying weather-related statistics.
"""


def get_data_from_openweather(link=CURRENT_OPENWEATHER_URI) -> str:
    """
    Fetch current weather data from the OpenWeatherMap API for Dublin.

    This function sends a GET request with hardcoded parameters (location, API key, units, and language)
    to retrieve current weather data.

    Parameters:
        link (str): The API endpoint URL to fetch data from. Defaults to CURRENT_OPENWEATHER_URI.

    Returns:
        str: The raw text response from the API containing weather data, or None if an exception occurs.
    """
    try:
        params = {
            "q": "Dublin,IE",
            "appid": WEATHER_KEY,
            "units": "metric",
            "lang": "en",
        }
        r = requests.get(link, params=params)
        r.raise_for_status()
        return r.text
    except:
        print(traceback.format_exc())
        return None


def save_weather_data_to_db(data: str, in_engine: sqla.engine.base.Connection) -> None:
    """
    Save weather data into the SQL database.

    This function processes the raw weather data obtained from the OpenWeatherMap API and saves
    it into the database by calling save_current_data_to_db(). Future enhancements may include
    scraping additional weather prediction data.

    Parameters:
        data (str): The raw weather data in JSON format.
        in_engine: The SQLAlchemy engine or connection object for database operations.

    Returns:
        None
    """
    print(data)
    save_current_data_to_db(data, in_engine)


def save_current_data_to_db(data: str, in_engine: sqla.engine.base.Connection) -> None:
    """
    Save current weather data into the SQL database.

    This function parses the current weather data from the OpenWeatherMap API and inserts it into the 'current'
    table. The table includes fields such as dt, feels_like, humidity, pressure, sunrise, sunset, temp, uvi,
    weather_id, wind_gust, wind_speed, rain_1h, and snow_1h.

    Parameters:
        data (str): The raw current weather data in JSON format.
        in_engine: The SQLAlchemy engine or connection object for database operations.

    Returns:
        None
    """
    try:
        current = json.loads(data)
        dt_current = datetime.datetime.fromtimestamp(current.get("dt"))
        weather_id = current.get("id") if "id" in current else "NULL"
        main = current.get("main", {})
        feels_like = main.get("feels_like") if "feels_like" in main else "NULL"
        humidity = main.get("humidity") if "humidity" in main else "NULL"
        pressure = main.get("pressure") if "pressure" in main else "NULL"
        temp = main.get("temp") if "temp" in main else "NULL"
        sys = current.get("sys", {})
        sunrise = datetime.datetime.fromtimestamp(sys.get("sunrise")) if "sunrise" in sys else "NULL"
        sunset = datetime.datetime.fromtimestamp(sys.get("sunset")) if "sunset" in sys else "NULL"
        wind = current.get("wind", {})
        wind_speed = wind.get("speed") if "speed" in wind else "NULL"
        wind_gust = wind.get("gust") if "gust" in wind else "NULL"
        rain = current.get("rain", {})
        rain_1h = rain.get("1h") if "1h" in rain else "NULL"
        uvi = "NULL"  # No information available
        snow_1h = "NULL"  # No information available
        query = f"""
            INSERT INTO current 
            (dt, feels_like, humidity, pressure, sunrise, sunset, temp, uvi, weather_id, wind_gust, wind_speed, rain_1h, snow_1h)
            VALUES (
                '{dt_current}', 
                {feels_like}, 
                {humidity}, 
                {pressure}, 
                '{sunrise}', 
                '{sunset}', 
                {temp}, 
                {uvi}, 
                {weather_id}, 
                {wind_gust}, 
                {wind_speed}, 
                {rain_1h}, 
                {snow_1h}
            );
        """
        execute_sql(query, in_engine)
    except Exception as e:
        print("Error saving current weather data:", e)
        print(traceback.format_exc())


def main_data_scrapper_weather(save_to_db: bool, engine: sqla.engine.base.Connection = None, text_file_path: os.path = None) -> None:
    """
    Main function for scraping weather data.

    This function continuously fetches weather data from the OpenWeatherMap API at fixed intervals (every 60 minutes)
    and saves the data either to the SQL database or to a CSV file, based on the save_to_db flag.
    It runs indefinitely in a loop.

    Parameters:
        save_to_db (bool): If True, saves the data to the SQL database; otherwise, saves to a CSV file.
        engine: The SQLAlchemy engine or connection object for database operations (required if save_to_db is True).
        text_file_path (str): The file path to save the data if not saving to the database.

    Returns:
        None
    """
    minutes = 60
    while True:
        weather_data = get_data_from_openweather()
        if weather_data:
            print("Weather Data Downloaded at ", datetime.datetime.now())
            if save_to_db:
                save_weather_data_to_db(weather_data, engine)
            else:
                save_data_to_file(weather_data, text_file_path)
        else:
            print("No Weather Data at ", datetime.datetime.now())
        time.sleep(60 * minutes)


if __name__ == "__main__":
    main_data_scrapper_weather()
