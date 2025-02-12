import requests
import traceback
import datetime
import time
import os
# import dbinfo
import json
import sqlalchemy as sqla
import traceback
import glob
import os
import requests
import time

from DublinBikes.Utils.params import *
from DublinBikes.Utils.sql_utils import get_sql_engine, execute_sql





def get_data_from_jcdecaux() -> str:
    """
    Function to get the data from the JCDecaux API.
    
    :return: the data from the API (text)
    """
    try:
        # r = requests.get(dbinfo.STATIONS_URI, params={"apiKey": dbinfo.JCKEY, "contract": dbinfo.NAME})
        r=requests.get(STATIONS_URI, params={"apiKey": JCKEY, "contract": NAME})
        return r.text
        
    except:
        print(traceback.format_exc())
        return None





def save_data_to_db(data: str, in_engine: sqla.engine.base.Connection) -> None:
    """
    Function to load the data into the database.
    
    :param data: the data to be loaded (text)
    :param in_engine: the engine to be used to load the data
    """
    save_stations_data_to_db(data, in_engine)
    # save_availability_data_to_db(data, in_engine)
    

        


def save_stations_data_to_db(data: str, in_engine: sqla.engine.base.Connection) -> None:
    """
    Function to load the data of the stations into the database.
    
            station_id INTEGER NOT NULL,
            address VARCHAR(128),
            banking INTEGER,
            bonus INTEGER,
            bike_stands INTEGER,
            name VARCHAR(128),
            position_lat FLOAT,
            position_lng FLOAT,
            PRIMARY KEY (number)
    """
    # Load the data from the text received from jcdecaux    
    stations = json.loads(data)
    
    for station in stations:
        
        v_station_id = station.get('number')  # Changed from number to station_id
        v_address = station.get('address')
        v_banking = int(station.get('banking'))
        v_bonus = int(station.get('bonus'))
        v_bikestands = int(station.get('bike_stands'))
        v_name = station.get('name')
        v_lat = station.get('position').get('lat')
        v_lng = station.get('position').get('lng')
        
        query = f"""
                INSERT INTO station (station_id, address, banking, bonus, bike_stands, name, position_lat, position_lng)
                VALUES ({v_station_id}, '{v_address}', {v_banking}, {v_bonus}, {v_bikestands}, '{v_name}', {v_lat}, {v_lng});
                """
        
        execute_sql(query, in_engine)





def save_availability_data_to_db(data: str, in_engine: sqla.engine.base.Connection) -> None:
    """
    Function to load the data of the stations into the database.
    
        station_id INTEGER NOT NULL,
        last_update DATETIME NOT NULL,
        available_bikes INTEGER,
        available_bike_stands INTEGER,
        status VARCHAR(128),
        PRIMARY KEY (number, last_update)
    """
    stations = json.loads(data)
    
    for station in stations:
        
        v_station_id = station.get('number') # Changed from number to station_id
        v_last_update = datetime.datetime.fromtimestamp(station.get('last_update')/1000)
        v_available_bikes = int(station.get('available_bikes'))
        v_available_bike_stands = int(station.get('available_bike_stands'))
        v_status = station.get('status')
        
        query = f"""
                INSERT INTO availability (station_id, last_update, available_bikes, available_bike_stands, status)
                VALUES ({v_station_id}, '{v_last_update}', {v_available_bikes}, {v_available_bike_stands}, '{v_status}');
                """
        
        execute_sql(query, in_engine)

 


def main_data_scrapper_bikes():
    
    # Determine if Data will be saved to the database or to a file
    # hardcoded for now: True if we want to save to db, False if we want to save to file
    save_to_db: bool = True
    
    if save_to_db: # If we connext to db: get the engine
        engine = get_sql_engine()
    
    while True:
        
        bikes_data = get_data_from_jcdecaux()
        
        if bikes_data:
            
            if save_to_db:
                save_data_to_db(bikes_data, engine)
            else:
                save_data_to_file(bikes_data)
            
        # For future: add logging info of failure to get data
        else:
            print("No Bike Data")
        
        time.sleep(5*60)







### Old code, when saving to file

def get_data_folder() -> str:
    """
    Ensure that the data folder exists and return the path to it.
    If it does not exist, create it.
    """
    
    data_folder: str = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
    
    if not os.path.exists(data_folder):
        os.mkdir(data_folder)
        print("Folder 'data' created!")

    return data_folder



def save_data_to_file(data: str)-> None:
    """
    Function to save the data to a text file.
    """
   
    data_folder: str = get_data_folder()
    time_stamp: str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    text_file: str = os.path.join(data_folder, f"bikes_{time_stamp}.json")

    with open(text_file, "w") as f:
        f.write(data)





if __name__ == "__main__":
    main_data_scrapper_bikes()