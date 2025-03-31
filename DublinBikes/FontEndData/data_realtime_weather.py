import datetime
import json
from DublinBikes.SQL_code.sql_utils import get_sql_engine
from DublinBikes.ScrappingData.scrapper_open_weather import get_data_from_openweather
from DublinBikes.FontEndData.manage_cache import clean_cache

"""
Improve this documentation:


Script Logic:
- Check if there is data in cache (data requested X mins ago, depending on the API)
- If yes: use it from the DB
- Else: Request it new, and save it to the DB

Daily delets of Cache
"""


def save_weather_data_to_cache_db(
    data: dict, forecast_type: str, target_datetime: datetime.datetime, return_row: bool
) -> None:
    """
    Saves weather data (both current and forecast) into the cache DB.

    Args:
        data (dict): The weather data dictionary (parsed from the API response).
        forecast_type (str): Type of forecast ('current', 'hourly', or 'daily').
        target_datetime (datetime.datetime): The target datetime for the weather info.
        return_row (bool): If we want the newly inserted to row to be returned or not
    """

    # First clean the cache form last days
    clean_cache()

    conn = get_sql_engine()

    try:
        # Extract common fields from the provided data.
        # For current weather, the API data structure might be slightly different from forecasts.
        # You can add logic here if the structure differs significantly.
        timestamp_requested = datetime.datetime.now()
        timestamp_weatherinfo = datetime.datetime.fromtimestamp(data.get("dt"))
        print("\n" + "TimeStampWeather Info: " + str(timestamp_weatherinfo) + "\n")
        main = data.get("main", {})
        feels_like = main.get("feels_like")
        humidity = main.get("humidity")
        pressure = main.get("pressure")
        temp = main.get("temp")

        # Sunrise and sunset might not be available in forecast data.
        sunrise = None
        sunset = None
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

        # Handle rain and snow data with potential key differences.
        if forecast_type == "current":
            rain_1h = data.get("rain", {}).get("1h")
            snow_1h = None  # Assuming not provided for current weather
        else:
            # For forecasts, rain and snow might be provided under a different key (e.g., "3h")
            rain_1h = data.get("rain", {}).get("3h")
            snow_1h = data.get("snow", {}).get("3h")

        # UV index might not be provided by the API.
        uvi = None

        # Weather ID (icon) extraction, ensuring we check that the list is not empty.
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
        print("Found a recent record – return it as a dict.")
        print(dict(row))
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
    Retrieve forecast weather data from cache if recently requested
    or else call the forecast API.

    forecast_type: "current", "hourly", or "daily"
    target_datetime: ISO formatted datetime string for which the forecast is valid
                     (for daily forecasts, you can store the date with a fixed time, e.g., noon)
    """

    # If the user selected to get the current weather: return the other function
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

        # Parse the API response.
        forecast_data = json.loads(data_text)
        forecast_list = forecast_data.get("list", [])

        matching_forecast = None
        # Extract all the forecasts: cache all to the DB and save one
        for forecast in forecast_list:

            print(forecast)
            print("------------------------------------------")
            entry_dt = datetime.datetime.fromtimestamp(forecast.get("dt"))

            # We check if the entry is within 1.5 hours of the requested time stamp
            # Why? Because the API gives us data of every 3 hours, this would be the colsest one
            if (
                abs((entry_dt - target_dt).total_seconds()) < 5470
            ):  # 3 hours = 5400 seconds, we put a bit more just in case
                matching_forecast = save_weather_data_to_cache_db(
                    forecast, forecast_type, target_datetime, return_row=True
                )

            else:
                save_weather_data_to_cache_db(
                    forecast, forecast_type, target_datetime, return_row=False
                )

        if not matching_forecast:
            return {"error": "No forecast found for the selected time."}

        print(matching_forecast)
        return matching_forecast
