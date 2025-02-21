from sqlalchemy import text
from DublinBikes.Utils.sql_utils import get_sql_engine
from DublinBikes.Scrapping.scrapper_jc_decaux import get_data_from_jcdecaux
from DublinBikes.Scrapping.scrapper_open_weather import get_data_from_openweather
import json

def get_station_data(station_id: int) -> dict:
    """
    Retrieve a station's complete data by joining the station and availability tables.
    Picks the availability record with the latest last_update and returns a flat dictionary.
    """
    engine = get_sql_engine()
    query = text("""
        SELECT s.station_id, s.address, s.banking, s.bonus, s.bike_stands, s.name,
               s.position_lat, s.position_lng,
               a.last_update, a.available_bikes, a.available_bike_stands, a.status
        FROM station s
        JOIN (
            SELECT station_id, MAX(last_update) AS last_update
            FROM availability
            GROUP BY station_id
        ) AS latest ON s.station_id = latest.station_id
        JOIN availability a ON a.station_id = latest.station_id AND a.last_update = latest.last_update
        WHERE s.station_id = :station_id;
    """)
    
    with engine.connect() as conn:
        row = conn.execute(query, {'station_id': station_id}).mappings().first()
    
    if row is None:
        return {}
    
    return dict(row)




def get_current_data() -> dict:
    """
    Obtain current data using the scrapper functions.
    The bikes data comes from the JCDecaux API and the weather data from OpenWeather.
    """
    weather_data_text = get_data_from_openweather()
    bikes_data_text = get_data_from_jcdecaux()
    
    try:
        weather_data = json.loads(weather_data_text) if weather_data_text else {}
    except Exception as e:
        weather_data = {"error": "Failed to parse weather data"}
    
    try:
        bikes_data = json.loads(bikes_data_text) if bikes_data_text else {}
    except Exception as e:
        bikes_data = {"error": "Failed to parse bikes data"}
        

        
    return {"weather": weather_data, "bikes": bikes_data}
