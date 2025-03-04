import csv
import json
from datetime import datetime
from sqlalchemy import text
from DublinBikes.Utils.sql_utils import get_sql_engine

def export_bikes_data(engine, output_file):
    """
    Exports bikes data to a CSV file.
    Uses a join between the station and availability tables (latest availability per station)
    and transforms the fields to match the CSV structure:
      number,contract_name,name,address,position,banking,bonus,
      bike_stands,available_bike_stands,available_bikes,status,last_update
    Note: contract_name is hardcoded as 'dublin' and last_update is converted to milliseconds.
    """
    
    query = text("""
        SELECT 
            s.station_id AS number,
            'dublin' AS contract_name,
            s.name,
            s.address,
            CONCAT("{'lat': ", s.position_lat, ", 'lng': ", s.position_lng, "}") AS position,
            IF(s.banking = 1, 'True', 'False') AS banking,
            IF(s.bonus = 1, 'True', 'False') AS bonus,
            s.bike_stands,
            a.available_bike_stands,
            a.available_bikes,
            a.status,
            UNIX_TIMESTAMP(a.last_update) * 1000 AS last_update
        FROM availability a 
        JOIN station s
        ON s.station_id = a.station_id
    """)
    with engine.connect() as conn:
        result = conn.execute(query)
        rows = result.fetchall()

    fieldnames = [
        'number', 'contract_name', 'name', 'address', 'position', 
        'banking', 'bonus', 'bike_stands', 'available_bike_stands', 
        'available_bikes', 'status', 'last_update'
    ]
    with open(output_file, mode='w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            row_data = dict(row._mapping)
            writer.writerow(row_data)


def export_weather_data(engine, output_file):
    """
    Exports weather data (from the 'current' table) to a CSV file.
    For each record in the last 24 hours, we build a CSV row that matches the CSV structure:
      coord, weather, base, main, visibility, wind, clouds, dt, sys, timezone, id, name, cod
    Since the SQL table doesn't store all fields required by the CSV format,
    some fields are hardcoded (e.g. coord, base, visibility, clouds, timezone, id, name, cod)
    and the 'main' field is built from temp, feels_like, pressure, and humidity.
    The dt, sunrise, and sunset fields are converted to epoch seconds.
    """
    query = text("""
        SELECT *
        FROM current
        WHERE dt >= NOW() - INTERVAL 1 DAY;
    """)
    with engine.connect() as conn:
        result = conn.execute(query)
        rows = result.fetchall()

    fieldnames = [
        'coord', 'weather', 'base', 'main', 'visibility', 'wind',
        'clouds', 'dt', 'sys', 'timezone', 'id', 'name', 'cod'
    ]
        
    with open(output_file, mode='w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            row_data = dict(row._mapping)
            # Convert DATETIME fields to epoch seconds
            dt_val = row_data.get('dt')
            dt_epoch = int(dt_val.timestamp()) if isinstance(dt_val, datetime) else 0
            sunrise_val = row_data.get('sunrise')
            sunrise_epoch = int(sunrise_val.timestamp()) if isinstance(sunrise_val, datetime) else 0
            sunset_val = row_data.get('sunset')
            sunset_epoch = int(sunset_val.timestamp()) if isinstance(sunset_val, datetime) else 0

            # Build the CSV fields as strings matching the CSV structure.
            coord = "{'lon': -6.2672, 'lat': 53.344}"
            weather = f"[{{'id': {row_data.get('weather_id', 0)}, 'main': 'Unknown', 'description': 'Unknown', 'icon': '01d'}}]"
            base = "stations"
            main_dict = {
                'temp': row_data.get('temp'),
                'feels_like': row_data.get('feels_like'),
                'temp_min': row_data.get('temp'),
                'temp_max': row_data.get('temp'),
                'pressure': row_data.get('pressure'),
                'humidity': row_data.get('humidity'),
                'sea_level': row_data.get('pressure'),
                'grnd_level': 1000
            }
            main_str = json.dumps(main_dict)
            visibility = "6000"
            wind = f"{{'speed': {row_data.get('wind_speed', 0)}, 'deg': 0}}"
            clouds = "{'all': 75}"
            dt_str = str(dt_epoch)
            sys_str = f"{{'type': 2, 'id': 0, 'country': 'IE', 'sunrise': {sunrise_epoch}, 'sunset': {sunset_epoch}}}"
            timezone_val = "0"
            # Use Dublin's city id as given in your CSV example.
            city_id = 2964574  
            name = "Dublin"
            cod = "200"

            csv_row = {
                'coord': coord,
                'weather': weather,
                'base': base,
                'main': main_str,
                'visibility': visibility,
                'wind': wind,
                'clouds': clouds,
                'dt': dt_str,
                'sys': sys_str,
                'timezone': timezone_val,
                'id': city_id,
                'name': name,
                'cod': cod
            }
            writer.writerow(csv_row)


def main():
    
    import os
    weather_export_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'weather_24h.csv')
    bikes_export_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'bikes_24h.csv')
    
    engine = get_sql_engine()
    
    # Check if the files already exist, do it if they don't
    if not os.path.exists(weather_export_file):
        export_weather_data(engine, weather_export_file)
        print("Exported weather data")

    
    if not os.path.exists(bikes_export_file):
        export_bikes_data(engine, bikes_export_file) 
        print("Exported bikes data")
        

if __name__ == '__main__':
    main()
