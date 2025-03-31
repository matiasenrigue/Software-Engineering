import requests
import traceback
import datetime
import time
import os
import json
import sqlalchemy as sqla

from DublinBikes.Utils.params import WEATHER_KEY, CURRENT_OPENWEATHER_URI
from DublinBikes.SQL_code.sql_utils import execute_sql
from DublinBikes.ScrapingData.local_scrapping import save_data_to_file


def get_data_from_openweather(link=CURRENT_OPENWEATHER_URI) -> str:
    """
    Function to get the weather data from the OpenWeatherMap API for Dublin.

    :return: the data from the API (text)
    """
    try:
        # Hardcoded parameters for Dublin, Ireland
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
    Function to load the weather data into the database.

    :param data: the data to be loaded (text)
    :param in_engine: the engine to be used to load the data
    """
    print(data)

    save_current_data_to_db(data, in_engine)  # Done
    # --> Future job: scrappe prediction data of weather (not needed now)


def save_current_data_to_db(data: str, in_engine: sqla.engine.base.Connection) -> None:
    """
    Function to load the current weather data into the database.

    Table structure (current):
        dt DATETIME NOT NULL,
        feels_like FLOAT,
        humidity INTEGER,
        pressure INTEGER,
        sunrise DATETIME,
        sunset DATETIME,
        temp FLOAT,
        uvi FLOAT,
        weather_id INTEGER,
        wind_gust FLOAT,
        wind_speed FLOAT,
        rain_1h FLOAT,
        snow_1h FLOAT,
        PRIMARY KEY (dt)
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
        sunrise = (
            datetime.datetime.fromtimestamp(sys.get("sunrise"))
            if "sunrise" in sys
            else "NULL"
        )
        sunset = (
            datetime.datetime.fromtimestamp(sys.get("sunset"))
            if "sunset" in sys
            else "NULL"
        )

        wind = current.get("wind", {})
        wind_speed = wind.get("speed") if "speed" in wind else "NULL"
        wind_gust = wind.get("gust") if "gust" in wind else "NULL"

        rain = current.get("rain", {})
        rain_1h = rain.get("1h") if "1h" in rain else "NULL"

        uvi = "NULL"  # No info
        snow_1h = "NULL"  # No info

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


def main_data_scrapper_weather(
    save_to_db: bool,
    engine: sqla.engine.base.Connection = None,
    text_file_path: os.path = None,
) -> None:
    """
    Main function for the weather data scrapper.
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

        else:  # For future: add logging info of failure to get data
            print("No Weather Data at ", datetime.datetime.now())

        time.sleep(60 * minutes)


if __name__ == "__main__":
    main_data_scrapper_weather()
