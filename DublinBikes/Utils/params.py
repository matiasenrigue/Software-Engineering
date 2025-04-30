import os
from dotenv import load_dotenv

load_dotenv()

DISABLE_LOGGING = True
APP_SECRET_KEY = os.environ.get("APP_SECRET_KEY")

# Where is the code running --> Local or AWS / Railway
LOCAL_RUNNING = True

# Dublin Bikes API
JCKEY = os.environ.get("JCKEY")
NAME = "dublin"
STATIONS_URI = "https://api.jcdecaux.com/vls/v1/stations"


# Open Weather API
WEATHER_KEY = os.environ.get("WEATHER_KEY")
CURRENT_OPENWEATHER_URI = "http://api.openweathermap.org/data/2.5/weather"

# Maps API Key
MAPS_API_KEY = os.environ.get("MAPS_API_KEY")



# Local DataBase
LOCAL_USER = "root"
LOCAL_PASSWORD = os.environ.get("LOCAL_PASSWORD")
LOCAL_DB = "dbbikes"
LOCAL_URI = "127.0.0.1"


