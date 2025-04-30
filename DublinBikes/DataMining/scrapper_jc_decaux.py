import requests
import traceback
import datetime
import time
import os
import json
import sqlalchemy as sqla
import traceback
import glob
import os
import requests
import time

from DublinBikes.Utils.params import *
from DublinBikes.SqlCode.sql_utils import execute_sql
from DublinBikes.DataMining.local_scrapping import save_data_to_file

"""
Module: scrapper_jc_decaux
--------------------------
This module handles the scraping of bike station data from the JCDecaux API.
It provides functions to fetch data from the API and to save the retrieved data into the SQL database.
The historical bike data obtained here is used for training machine learning models
to predict station availability and for displaying availability statistics.
"""

import logging

logger = logging.getLogger(__name__)


def get_data_from_jcdecaux() -> str:
    """
    Fetch bike station data from the JCDecaux API.

    This function sends a GET request to the JCDecaux API using predefined parameters (API key and contract name).
    
    Returns:
        str: The raw text response from the API containing bike station data, or None if an exception occurs.
    """
    try:
        r = requests.get(STATIONS_URI, params={"apiKey": JCKEY, "contract": NAME})
        return r.text
    except:
        logger.info(traceback.format_exc())
        return None


def save_bikes_data_to_db(data: str, in_engine: sqla.engine.base.Connection) -> None:
    """
    Save bike station data into the SQL database.

    This function processes the raw data from the JCDecaux API and saves it into the database.
    It currently focuses on saving availability data by calling save_availability_data_to_db().

    Parameters:
        data (str): The raw bike station data in JSON format.
        in_engine: The SQLAlchemy engine or connection object for database operations.

    Returns:
        None
    """
    save_availability_data_to_db(data, in_engine)


def save_stations_data_to_db(data: str, in_engine: sqla.engine.base.Connection) -> None:
    """
    Save station information into the SQL database.

    This function parses the bike station data from the JCDecaux API and inserts station details into the 'station' table.
    The table structure includes fields such as station_id, address, banking, bonus, bike_stands, name, position_lat, and position_lng.

    Parameters:
        data (str): The raw bike station data in JSON format.
        in_engine: The SQLAlchemy engine or connection object for database operations.

    Returns:
        None
    """
    stations = json.loads(data)
    for station in stations:
        v_station_id = station.get("number")  # Changed from number to station_id
        v_address = station.get("address")
        v_banking = int(station.get("banking"))
        v_bonus = int(station.get("bonus"))
        v_bikestands = int(station.get("bike_stands"))
        v_name = station.get("name")
        v_lat = station.get("position").get("lat")
        v_lng = station.get("position").get("lng")
        query = f"""
                INSERT INTO station (station_id, address, banking, bonus, bike_stands, name, position_lat, position_lng)
                VALUES ({v_station_id}, '{v_address}', {v_banking}, {v_bonus}, {v_bikestands}, '{v_name}', {v_lat}, {v_lng});
                """
        execute_sql(query, in_engine)


def save_availability_data_to_db(data: str, in_engine: sqla.engine.base.Connection) -> None:
    """
    Save bike station availability data into the SQL database.

    This function parses the raw bike station data from the JCDecaux API and inserts availability information
    (including station_id, last_update, available_bikes, available_bike_stands, and status) into the 'availability' table.

    Parameters:
        data (str): The raw bike station data in JSON format.
        in_engine: The SQLAlchemy engine or connection object for database operations.

    Returns:
        None
    """
    stations = json.loads(data)
    for station in stations:
        v_station_id = station.get("number")  # Changed from number to station_id
        v_last_update = datetime.datetime.fromtimestamp(station.get("last_update") / 1000)
        v_available_bikes = int(station.get("available_bikes"))
        v_available_bike_stands = int(station.get("available_bike_stands"))
        v_status = station.get("status")
        query = f"""
                INSERT INTO availability (station_id, last_update, available_bikes, available_bike_stands, status)
                VALUES ({v_station_id}, '{v_last_update}', {v_available_bikes}, {v_available_bike_stands}, '{v_status}');
                """
        execute_sql(query, in_engine)


def main_data_scrapper_bikes(save_to_db: bool, engine: sqla.engine.base.Connection = None, text_file_path: os.path = None) -> None:
    """
    Main function for scraping bike station data.

    This function continuously fetches bike station data from the JCDecaux API at fixed intervals (every 5 minutes)
    and saves the data either to the SQL database or to a CSV file, based on the save_to_db flag.
    It runs indefinitely in a loop.

    Parameters:
        save_to_db (bool): If True, saves the data to the SQL database; otherwise, saves to a CSV file.
        engine: The SQLAlchemy engine or connection object for database operations (required if save_to_db is True).
        text_file_path (str): The file path to save the data if not saving to the database.

    Returns:
        None
    """
    minutes = 5
    while True:
        bikes_data = get_data_from_jcdecaux()
        if bikes_data:
            logger.info("Bike Data Downloaded at ", datetime.datetime.now())
            if save_to_db:
                save_bikes_data_to_db(bikes_data, engine)
            else:
                save_data_to_file(bikes_data, text_file_path)

        else:  
            logger.info("No Bike Data at ", datetime.datetime.now())

        time.sleep(60 * minutes)


if __name__ == "__main__":
    main_data_scrapper_bikes()
