from sqlalchemy import text
from DublinBikes.SqlCode.sql_utils import get_sql_engine

"""
Module: data_loader_SQL
------------------------
This module provides functions for retrieving bike station data from a SQL database.
These functions query tables such as 'FetchedBikesData', 'station', and 'availability' to 
retrieve station details and daily availability records.
Note: Although these functions are not currently used, they are kept for future reference.
"""


def get_station_data(station_id: int) -> dict:
    """
    Retrieve the latest available data for a specific station.

    This function queries the 'FetchedBikesData' table to obtain a single record for the specified station.
    It sorts the results by 'last_update' in descending order and returns the most recent record as a dictionary.

    Parameters:
        station_id (int): The unique identifier of the station.

    Returns:
        dict: A dictionary containing station data such as station_id, address, banking, bonus, bike stands,
              name, position coordinates, last update time, available bikes, available bike stands, and status.
    """
    query = """
        SELECT station_id, address, banking, bonus, bike_stands, name,
               position_lat, position_lng,
               last_update, available_bikes, available_bike_stands, status
        FROM FetchedBikesData 
        WHERE station_id = :station_id
        Order By last_update DESC
        LIMIT 1;
    """
    conn = get_sql_engine()
    try:
        cursor = conn.cursor()
        cursor.execute(query, {"station_id": station_id})
        rows = cursor.fetchall()
        stations = [dict(row) for row in rows]
        return stations
    finally:
        conn.close()


def get_all_stations_data_SQL() -> list:
    """
    Retrieve data for all bike stations.

    This function queries the 'station' table and returns a list of dictionaries,
    each containing data for a bike station. The position coordinates are grouped in a dictionary.

    Returns:
        list: A list of dictionaries, each representing a bike station with details such as station_id,
              address, banking, bonus, bike stands, name, and position coordinates.
    """
    conn = get_sql_engine()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM station")
        rows = cursor.fetchall()
        stations = []
        for row in rows:
            station = {
                "station_id": row[0],
                "address": row[1],
                "banking": row[2],
                "bonus": row[3],
                "bike_stands": row[4],
                "name": row[5],
                "position": {"lat": row[6], "lng": row[7]},
            }
            stations.append(station)
        return stations
    finally:
        conn.close()


def get_one_station_data(station_id: int) -> dict:
    """
    Retrieve data for a single bike station.

    This function queries the 'station' table for a specific station identified by station_id.
    If the station is found, the function returns its data as a dictionary; otherwise, it returns an empty dictionary.

    Parameters:
        station_id (int): The unique identifier of the station.

    Returns:
        dict: A dictionary containing the station's data, or an empty dictionary if not found.
    """
    conn = get_sql_engine()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM station WHERE station_id = :station_id",
            {"station_id": station_id},
        )
        row = cursor.fetchone()
        return dict(row) if row is not None else {}
    finally:
        conn.close()


def get_station_availability_daily(station_id: int) -> list:
    """
    Retrieve daily availability records for a specific station.

    This function queries the 'availability' table to obtain all availability records for the specified station
    for the date '2025-03-03'. The results are ordered by the 'last_update' timestamp in ascending order.

    Parameters:
        station_id (int): The unique identifier of the station.

    Returns:
        list: A list of dictionaries, each representing an availability record with fields for last_update,
              available_bikes, and available_bike_stands.
    """
    query = """
        SELECT last_update, available_bikes, available_bike_stands
        FROM availability
        WHERE station_id = :station_id
            AND DATE(last_update) = '2025-03-03'
        ORDER BY last_update ASC;
    """
    conn = get_sql_engine()
    try:
        cursor = conn.cursor()
        cursor.execute(query, {"station_id": station_id})
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()
