from DublinBikes.ScrappingData.scrapper_jc_decaux import get_data_from_jcdecaux
from DublinBikes.ScrappingData.scrapper_open_weather import get_data_from_openweather
import json


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