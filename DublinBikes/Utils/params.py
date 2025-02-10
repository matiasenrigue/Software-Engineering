from dotenv import load_dotenv
import os

# Automatically load variables from the .env file in the current directory.
load_dotenv()


# Dublin Bikes API
JCKEY = 'c7d3631426d8d7f599c2d73bfce5ebcacc525445'
NAME = "dublin"
STATIONS_URI = "https://api.jcdecaux.com/vls/v1/stations"


# DataBase: AWS RDS
USER = 'matiasenrigue'
PASSWORD = 'sxTjHMpzPco5zeVCUeN9'
PORT = "3306"
DB = 'dbbikes'
URI = 'dublin-bikes-data.cbq40u2g88do.eu-north-1.rds.amazonaws.com'

# Local DataBase
LOCAL_USER = "root"
LOCAL_PASSWORD = os.environ.get("LOCAL_PASSWORD")
LOCAL_DB = "dbbikes"
LOCAL_URI = "127.0.0.1"


# mysql -h dublin-bikes-data.cbq40u2g88do.eu-north-1.rds.amazonaws.com -P 3306 -u matiasenrigue -p



