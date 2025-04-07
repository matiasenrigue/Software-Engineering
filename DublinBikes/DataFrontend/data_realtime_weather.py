import datetime
import json
from DublinBikes.SqlCode.sql_utils import get_sql_engine
from DublinBikes.DataMining.scrapper_open_weather import get_data_from_openweather

"""
Module: data_realtime_weather
-----------------------------
This module provides functions for handling real-time weather data.
It includes functionality for saving weather data to the cache database and retrieving current or forecast weather data.
The module also implements cache cleaning to remove outdated records.

Script Logic:
- Check if weather data is available in cache (data requested within a specified time interval).
- If available, return cached data.
- Otherwise, fetch new data from the OpenWeather API, save it to the cache, and return the data.
- The cache is cleaned daily to remove outdated records.
"""


def save_weather_data_to_cache_db(
    data: dict, forecast_type: str, target_datetime: datetime.datetime, return_row: bool
) -> None:
    """
    Save weather data to the cache database.

    This function saves both current and forecast weather data into the 'FetchedWeatherData' table.
    Before inserting new data, it cleans the cache to remove outdated records.
    Depending on the forecast type, it extracts relevant fields from the provided data dictionary.
    If 'return_row' is True, the function returns the newly inserted row as a dictionary.

    Parameters:
        data (dict): The weather data parsed from the API response.
        forecast_type (str): The type of forecast ('current', 'hourly', or 'daily').
        target_datetime (datetime.datetime): The target datetime for the weather forecast.
        return_row (bool): Whether to return the newly inserted row.

    Returns:
        dict: The inserted weather data row as a dictionary if return_row is True; otherwise, None.
    """
    conn = get_sql_engine()
    try:
        timestamp_requested = datetime.datetime.now()
        timestamp_weatherinfo = datetime.datetime.fromtimestamp(data.get("dt"))
        main = data.get("main", {})
        feels_like = main.get("feels_like")
        humidity = main.get("humidity")
        pressure = main.get("pressure")
        temp = main.get("temp")
        sunrise = None # No info for forecast
        sunset = None # No info for forecast
        if forecast_type == "current":
            sys_data = data.get("sys", {})
            sunrise = (
                datetime.datetime.fromtimestamp(sys_data.get("sunrise"))
                if sys_data.get("sunrise")
                else None
            )
            sunset = (
                datetime.datetime.fromtimestamp(sys_data.get("sunset"))
                if sys_data.get("sunset")
                else None
            )
        wind = data.get("wind", {})
        wind_speed = wind.get("speed")
        wind_gust = wind.get("gust")
        if forecast_type == "current":
            rain_1h = data.get("rain", {}).get("1h")
            snow_1h = None
        else:
            rain_1h = data.get("rain", {}).get("3h")
            snow_1h = data.get("snow", {}).get("3h")
        uvi = None
        weather_list = data.get("weather", [])
        weather_id = weather_list[0].get("icon") if weather_list else None
        insert_query = """
            INSERT INTO FetchedWeatherData (
                timestamp_requested, timestamp_weatherinfo, forecast_type, target_datetime,
                feels_like, humidity, pressure, sunrise, sunset, temp, uvi, weather_id,
                wind_gust, wind_speed, rain_1h, snow_1h
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """
        cursor = conn.cursor()
        cursor.execute(
            insert_query,
            (
                timestamp_requested,
                timestamp_weatherinfo,
                forecast_type,
                target_datetime,
                feels_like,
                humidity,
                pressure,
                sunrise,
                sunset,
                temp,
                uvi,
                weather_id,
                wind_gust,
                wind_speed,
                rain_1h,
                snow_1h,
            ),
        )
        conn.commit()
        
        # If we want to return the row we just inserted
        if return_row:
            cursor.execute("SELECT last_insert_rowid();")
            inserted_rowid = cursor.fetchone()[0]
            cursor.execute(
                "SELECT * FROM FetchedWeatherData WHERE rowid = ?", (inserted_rowid,)
            )
            row = cursor.fetchone()
            return dict(row) if row else {}
    finally:
        conn.close()


def get_current_weather_data():
    """
    Retrieve current weather data from the cache or from the OpenWeather API.

    This function attempts to retrieve current weather data from the cache if a record was requested
    within the last 15 minutes. If a recent record is found, it returns it as a dictionary.
    Otherwise, it fetches new data from the OpenWeather API, saves it to the cache, and returns the new record.

    Returns:
        dict: A dictionary containing current weather data, or an error message if data could not be fetched.
    """
    conn = get_sql_engine()
    try:
        fifteen_minutes_ago = datetime.datetime.now() - datetime.timedelta(minutes=15)
        query = """
            SELECT * FROM FetchedWeatherData
            WHERE forecast_type = 'current' AND timestamp_requested >= ?
            ORDER BY timestamp_requested DESC LIMIT 1;
        """
        cursor = conn.cursor()
        cursor.execute(query, (fifteen_minutes_ago,))
        row = cursor.fetchone()
    finally:
        cursor.close()
    if row:
        return dict(row)
    else:
        # No recent record: fetch new data from OpenWeather.
        data_text = get_data_from_openweather()
        if data_text:
            current = json.loads(data_text)
            dt_current = datetime.datetime.fromtimestamp(current.get("dt"))
            return save_weather_data_to_cache_db(
                current, "current", dt_current, return_row=True
            )
        else:
            return {"error": "Unable to fetch weather data"}


def get_forecast_weather_data(forecast_type: str, target_datetime: str) -> dict:
    """
    Retrieve forecast weather data from the cache or from the OpenWeather API.

    For forecast_type 'current', this function simply returns the current weather data.
    For other forecast types ('hourly' or 'daily'), it first attempts to retrieve a matching forecast
    from the cache that is within a specified time range of the target datetime.
    If a matching forecast is not found, it fetches forecast data from the API, caches all forecasts,
    and returns the forecast that best matches the target datetime.

    Parameters:
        forecast_type (str): The type of forecast ('current', 'hourly', or 'daily').
        target_datetime (str): The ISO formatted datetime string representing the target time for the forecast.

    Returns:
        dict: A dictionary containing the forecast weather data, or an error message if no matching forecast is found.
    """
    if forecast_type == "current":
        return get_current_weather_data()
    target_dt = datetime.datetime.fromisoformat(target_datetime)
    now = datetime.datetime.now()
    cache_interval = datetime.timedelta(hours=1)
    engine = get_sql_engine()
    try:
        cutoff = now - cache_interval
        query = """
            SELECT *, ABS(strftime('%s', timestamp_weatherinfo) - strftime('%s', ?)) AS time_diff
            FROM FetchedWeatherData
            WHERE forecast_type = ?
            AND timestamp_requested >= ?
            AND ABS(strftime('%s', timestamp_weatherinfo) - strftime('%s', ?)) <= 10800
            ORDER BY time_diff ASC
            LIMIT 1;
        """
        cursor = engine.cursor()
        cursor.execute(query, (target_dt, forecast_type, cutoff, target_dt))
        row = cursor.fetchone()
    finally:
        engine.close()
    if row:
        return dict(row)
    
    # Else, ask the API, and save cache data from the API for all the forecasts given
    else:
        api_url = "https://api.openweathermap.org/data/2.5/forecast"
        data_text = get_data_from_openweather(link=api_url)
        if not data_text:
            return {"error": "Unable to fetch forecast data from API"}
        forecast_data = json.loads(data_text)
        forecast_list = forecast_data.get("list", [])
        matching_forecast = None
        
        # Extract all the forecasts: cache all to the DB and save one
        for forecast in forecast_list:
            entry_dt = datetime.datetime.fromtimestamp(forecast.get("dt"))

            # We check if the entry is within 1.5 hours of the requested time stamp
            # Why? Because the API gives us data of every 3 hours, this would be the colsest one
            # 3 hours = 5400 seconds, we put a bit more just in case
            if abs((entry_dt - target_dt).total_seconds()) < 5470:
                matching_forecast = save_weather_data_to_cache_db(
                    forecast, forecast_type, target_datetime, return_row=True
                )
            else:
                save_weather_data_to_cache_db(
                    forecast, forecast_type, target_datetime, return_row=False
                )
        if not matching_forecast:
            return {"error": "No forecast found for the selected time."}
        return matching_forecast
