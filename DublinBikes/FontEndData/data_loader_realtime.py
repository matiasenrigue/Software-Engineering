import datetime
import json
from DublinBikes.SQL_code.sql_utils import get_sql_engine
from DublinBikes.ScrappingData.scrapper_open_weather import get_data_from_openweather


# def get_current_data() -> dict:
#     """
#     Obtain current data using the scrapper functions.
#     The bikes data comes from the JCDecaux API and the weather data from OpenWeather.
#     """
#     weather_data_text = get_data_from_openweather()
#     bikes_data_text = get_data_from_jcdecaux()
    
#     try:
#         weather_data = json.loads(weather_data_text) if weather_data_text else {}
#     except Exception as e:
#         weather_data = {"error": "Failed to parse weather data"}
    
#     try:
#         bikes_data = json.loads(bikes_data_text) if bikes_data_text else {}
#     except Exception as e:
#         bikes_data = {"error": "Failed to parse bikes data"}
        

        
#     return {"weather": weather_data, "bikes": bikes_data}




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
        if row:
            print("Found a recent record – return it as a dict.")
            print(dict(row))
            # Found a recent record – return it as a dict.
            return dict(row)
        
        else:
            # No recent record: fetch new data from OpenWeather.
            data_text = get_data_from_openweather()
            
            if data_text:
                current = json.loads(data_text)
                dt_current = datetime.datetime.fromtimestamp(current.get("dt"))
                main = current.get("main", {})
                feels_like = main.get("feels_like")
                humidity = main.get("humidity")
                pressure = main.get("pressure")
                temp = main.get("temp")
                sys_data = current.get("sys", {})
                sunrise = datetime.datetime.fromtimestamp(sys_data.get("sunrise")) if sys_data.get("sunrise") else None
                sunset = datetime.datetime.fromtimestamp(sys_data.get("sunset")) if sys_data.get("sunset") else None
                wind = current.get("wind", {})
                wind_speed = wind.get("speed")
                wind_gust = wind.get("gust")
                rain = current.get("rain", {})
                rain_1h = rain.get("1h")
                uvi = None  # not provided by this API call
                snow_1h = None
                timestamp_requested = datetime.datetime.now()
                is_current_weather = 1  # true
                weather_id = current.get("weather")[0].get("icon")
                
                insert_query = """
                INSERT INTO FetchedWeatherData (
                    timestamp_requested, timestamp_weatherinfo, forecast_type, target_datetime,
                    feels_like, humidity, pressure, sunrise, sunset, temp, uvi, weather_id,
                    wind_gust, wind_speed, rain_1h, snow_1h
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """
                
                cursor.execute(insert_query, 
                               (timestamp_requested, dt_current, "current", dt_current, 
                                feels_like, humidity, pressure, sunrise, sunset, temp, uvi, weather_id, 
                                wind_gust, wind_speed, rain_1h, snow_1h))

                
                conn.commit()
                return {
                    "timestamp_requested": timestamp_requested.isoformat(),
                    "timestamp_weatherinfo": dt_current.isoformat(),
                    "forecast_type": "current",
                    "target_datetime": dt_current.isoformat(),
                    "feels_like": feels_like,
                    "humidity": humidity,
                    "pressure": pressure,
                    "sunrise": sunrise.isoformat() if sunrise else None,
                    "sunset": sunset.isoformat() if sunset else None,
                    "temp": temp,
                    "uvi": uvi,
                    "weather_id": weather_id,
                    "wind_gust": wind_gust,
                    "wind_speed": wind_speed,
                    "rain_1h": rain_1h,
                    "snow_1h": snow_1h,
                }                    

            else:
                return {"error": "Unable to fetch weather data"}
    finally:
        conn.close()




def get_forecast_weather_data(forecast_type: str, target_datetime: str) -> dict:
    """
    Retrieve forecast weather data from cache if recently requested
    or else call the forecast API.

    forecast_type: "current", "hourly", or "daily"
    target_datetime: ISO formatted datetime string for which the forecast is valid
                     (for daily forecasts, you can store the date with a fixed time, e.g., noon)
    """
    
    print("hey")
    
    target_dt = datetime.datetime.fromisoformat(target_datetime)
    now = datetime.datetime.now()
    
    # Set caching interval to 3 hours for 3‑hour forecasts.
    cache_interval = datetime.timedelta(hours=3)

    # Set caching intervals based on forecast type.
    if forecast_type == "current":
        cache_interval = datetime.timedelta(minutes=30)
    elif forecast_type == "hourly":
        cache_interval = datetime.timedelta(hours=3)
    else:
        return {"error": "Invalid forecast type"}

    engine = get_sql_engine()
    try:
        cutoff = now - cache_interval
        query = """
            SELECT * FROM FetchedWeatherData
            WHERE forecast_type = ?
              AND target_datetime = ?
              AND timestamp_requested >= ?
            ORDER BY timestamp_requested DESC LIMIT 1;
        """
        cursor = engine.cursor()
        cursor.execute(query, (forecast_type, target_dt, cutoff))
        row = cursor.fetchone()
        if row:
            # Return cached forecast data.
            return dict(row)
        else:
            
            if forecast_type != "current":
            
                api_url = "https://api.openweathermap.org/data/2.5/forecast"
            
                data_text = get_data_from_openweather(link=api_url)
                if not data_text:
                    return {"error": "Unable to fetch forecast data from API"}

                # Parse the API response.
                forecast_data = json.loads(data_text)
                # Extract the forecast for the target datetime.
                # (You’ll need to filter the returned list by matching dt or dt_txt to your target_dt.)
                # For example:
                forecast_list = forecast_data.get("list", [])
                matching_forecast = None
                for entry in forecast_list:
                    # Assume each entry has a field 'dt' (unix timestamp) or 'dt_txt'
                    entry_dt = datetime.datetime.fromtimestamp(entry.get("dt"))
                    # A simple equality test may need to be adjusted (e.g., allow a few minutes of leeway)
                    if abs((entry_dt - target_dt).total_seconds()) < 5400:  # within 1.5 hours
                        matching_forecast = entry
                        break
                if not matching_forecast:
                    return {"error": "No forecast found for the selected time."}
                
                # Save the forecast data in the DB.
                timestamp_requested = now
                # Use the forecast's reported time (converted from API) as timestamp_weatherinfo.
                timestamp_weatherinfo = datetime.datetime.fromtimestamp(matching_forecast.get("dt"))
                # Extract weather fields from matching_forecast; here we assume similar structure to current.
                feels_like = matching_forecast.get("main", {}).get("feels_like")
                humidity = matching_forecast.get("main", {}).get("humidity")
                pressure = matching_forecast.get("main", {}).get("pressure")
                temp = matching_forecast.get("main", {}).get("temp")
                wind_speed = matching_forecast.get("wind", {}).get("speed")
                wind_gust = matching_forecast.get("wind", {}).get("gust")
                # For forecasts, sunrise/sunset may come from a separate part of the response.
                sunrise = None
                sunset = None
                rain_1h = matching_forecast.get("rain", {}).get("3h")
                snow_1h = matching_forecast.get("snow", {}).get("3h")
                uvi = None  # if not provided
                weather_id = matching_forecast.get("weather", [{}])[0].get("icon")

                insert_query = """
                INSERT INTO FetchedWeatherData (
                    timestamp_requested, timestamp_weatherinfo, forecast_type, target_datetime,
                    feels_like, humidity, pressure, sunrise, sunset, temp, uvi, weather_id,
                    wind_gust, wind_speed, rain_1h, snow_1h
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """
                                
                cursor.execute(insert_query, (
                    timestamp_requested, timestamp_weatherinfo, forecast_type, target_dt,
                    feels_like, humidity, pressure,
                    sunrise, sunset, temp, uvi, weather_id,
                    wind_gust, wind_speed, rain_1h, snow_1h
                ))
                engine.commit()
                # Return the newly saved forecast data.
                return {
                    "timestamp_requested": timestamp_requested.isoformat(),
                    "timestamp_weatherinfo": timestamp_weatherinfo.isoformat(),
                    "forecast_type": forecast_type,
                    "target_datetime": target_dt.isoformat(),
                    "feels_like": feels_like,
                    "humidity": humidity,
                    "pressure": pressure,
                    "temp": temp,
                    "wind_speed": wind_speed,
                    "wind_gust": wind_gust,
                    "rain_1h": rain_1h,
                    "snow_1h": snow_1h,
                    "weather_id": weather_id
                }
            else:
                # For forecast_type "current", you can call your existing get_current_weather_data
                return get_current_weather_data()
    finally:
        engine.close()





