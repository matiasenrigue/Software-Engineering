import os

# Automatically load variables from the .env file in the current directory.
# --> Disabled for now because can't make it work on amazon
# from dotenv import load_dotenv
# load_dotenv()


# Where is the code running --> Local or AWS / Railway 
LOCAL_RUNNING = True

# Dublin Bikes API
JCKEY = 'c7d3631426d8d7f599c2d73bfce5ebcacc525445'
NAME = "dublin"
STATIONS_URI = "https://api.jcdecaux.com/vls/v1/stations"


# Open Weather API
WEATHER_KEY = "dbfc50e69bbbfe9e2bb4117a52072796"
CURRENT_OPENWEATHER_URI = "http://api.openweathermap.org/data/2.5/weather"

# Maps API Key
MAPS_API_KEY = "AIzaSyARH2XSKUGhfUzApps65pDq4AZdaXoeYjY"


# DataBase: Railway
USER = 'root'
PASSWORD = 'gxtuFFUfsKIGieRySYwKLNYgrFYoPZuc'
PORT = '3306'
DB = 'railway'
URI = 'mysql.railway.internal'
WHOLE_URI = 'mysql+mysqlconnector://root:gxtuFFUfsKIGieRySYwKLNYgrFYoPZuc@centerbeam.proxy.rlwy.net:26648/railway'


# Local DataBase
LOCAL_USER = "root"
LOCAL_PASSWORD = "12345678" # os.environ.get("LOCAL_PASSWORD")
LOCAL_DB = "dbbikes"
LOCAL_URI = "127.0.0.1"


# mysql -h dublin-bikes-data.cbq40u2g88do.eu-north-1.rds.amazonaws.com -P 3306 -u matiasenrigue -p



