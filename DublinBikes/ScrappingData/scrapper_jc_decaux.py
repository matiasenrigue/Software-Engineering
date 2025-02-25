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
from DublinBikes.Utils.sql_utils import execute_sql
from DublinBikes.ScrappingData.local_scrapping import save_data_to_file





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





def save_bikes_data_to_db(data: str, in_engine: sqla.engine.base.Connection) -> None:
    """
    Function to load the data into the database.
    
    :param data: the data to be loaded (text)
    :param in_engine: the engine to be used to load the data
    """
    # save_stations_data_to_db(data, in_engine)
    save_availability_data_to_db(data, in_engine)
    

        


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

 


def main_data_scrapper_bikes(
            save_to_db: bool, 
            engine: sqla.engine.base.Connection = None,
            text_file_path : os.path = None
    ) -> None:
    """
    Main function for the bikes data scrapper.
    """
    
    minutes = 5
    
    while True:
        bikes_data = get_data_from_jcdecaux()
        
        if bikes_data:
            
            print("Bike Data Downloaded at ", datetime.datetime.now())
            
            if save_to_db:
                save_bikes_data_to_db(bikes_data, engine)
            else:
                save_data_to_file(bikes_data, text_file_path)
            
        else:    # For future: add logging info of failure to get data
            print("No Bike Data at ", datetime.datetime.now())
            
        
        time.sleep(60 * minutes)




if __name__ == "__main__":
    main_data_scrapper_bikes()