import csv
import ast
import os
from datetime import datetime

def read_bike_data_csv():
    """
    Reads the bike station data from bikes_data.csv and returns a list of stations.
    Each station contains: name, address, and bike_stands.
    """
    data_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'bikes_data.csv')
    stations = []
    with open(data_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            station = {
                'name': row.get('name'),
                'address': row.get('address'),
                'bike_stands': row.get('bike_stands'),
                'station_id': row.get('number')
            }
            stations.append(station)
    return stations


def read_weather_data_csv():
    """
    Reads the weather data from weather_data.csv (first row) and returns a dict with:
    temperature, description, sunrise, and sunset.
    Uses ast.literal_eval to parse stringified Python dictionaries/lists.
    """
    data_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'weather_data.csv')
    with open(data_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        row = next(reader, None)
        if row:
            # Parse the 'main' field to get temperature.
            main_data = ast.literal_eval(row.get('main'))
            temperature = main_data.get('temp')
            
            # Parse the 'weather' field to get description.
            weather_list = ast.literal_eval(row.get('weather'))
            description = weather_list[0].get('description') if weather_list and isinstance(weather_list, list) else ''
            
            # Parse the 'sys' field to get sunrise and sunset times.
            sys_data = ast.literal_eval(row.get('sys'))
            sunrise_ts = sys_data.get('sunrise')
            sunset_ts = sys_data.get('sunset')
            sunrise = datetime.fromtimestamp(sunrise_ts).strftime('%I:%M %p') if sunrise_ts else ''
            sunset = datetime.fromtimestamp(sunset_ts).strftime('%I:%M %p') if sunset_ts else ''
            
            return {
                'temperature': temperature,
                'description': description,
                'sunrise': sunrise,
                'sunset': sunset
            }
    return {}
