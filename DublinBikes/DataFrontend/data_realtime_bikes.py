import datetime
import json
from DublinBikes.SqlCode.sql_utils import get_sql_engine
from DublinBikes.DataMining.scrapper_jc_decaux import get_data_from_jcdecaux
from DublinBikes.DataFrontend.manage_cache import clean_cache

"""
Module: data_realtime_bikes
---------------------------
This module provides functions for handling real-time bike data.
It includes functionality for saving bike data to the cache database and retrieving current bike data,
either from the cache or directly from the bikes API.
"""


def save_bikes_data_to_cache_db(bikes_data: list, return_rows: bool = True) -> list:
    """
    Save bike station data to the cache database.

    This function inserts bike station data obtained from the bikes API into the 'FetchedBikesData' table.
    All records are inserted with a single timestamp (time_requested). Optionally, the inserted records can
    be returned as a list of dictionaries.

    Parameters:
        bikes_data (list): A list of dictionaries representing bike station data from the API.
        return_rows (bool): If True, returns the inserted records; otherwise, returns an empty list.

    Returns:
        list: A list of dictionaries representing the inserted bike station records (if return_rows is True).
    """
    # Clean outdated cache records before saving new data.
    clean_cache()
    
    conn = get_sql_engine()
    inserted_records = []
    try:
        time_requested = datetime.datetime.now()
        cursor = conn.cursor()
        for station in bikes_data:
            station_id = station.get("number")
            available_bikes = station.get("available_bikes")
            available_bike_stands = station.get("available_bike_stands")
            status = station.get("status")
            last_update_ms = station.get("last_update")
            last_update = (
                datetime.datetime.fromtimestamp(last_update_ms / 1000)
                if last_update_ms
                else None
            )
            address = station.get("address")
            banking = station.get("banking")
            bonus = station.get("bonus")
            bike_stands = station.get("bike_stands")
            name = station.get("name")
            position = station.get("position", {})
            position_lat = position.get("lat")
            position_lng = position.get("lng")
            insert_query = """
            INSERT INTO FetchedBikesData (
                time_requested, station_id, available_bikes, available_bike_stands, status, last_update,
                address, banking, bonus, bike_stands, name, position_lat, position_lng
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """
            cursor.execute(
                insert_query,
                (
                    time_requested,
                    station_id,
                    available_bikes,
                    available_bike_stands,
                    status,
                    last_update,
                    address,
                    banking,
                    bonus,
                    bike_stands,
                    name,
                    position_lat,
                    position_lng,
                ),
            )
            if return_rows:
                inserted_records.append(
                    {
                        "time_requested": time_requested,
                        "station_id": station_id,
                        "available_bikes": available_bikes,
                        "available_bike_stands": available_bike_stands,
                        "status": status,
                        "last_update": last_update,
                        "address": address,
                        "banking": banking,
                        "bonus": bonus,
                        "bike_stands": bike_stands,
                        "name": name,
                        "position": {"lat": position_lat, "lng": position_lng},
                    }
                )
        conn.commit()
        return inserted_records
    finally:
        conn.close()


def get_current_bikes_data():
    """
    Retrieve current bike station data.

    This function checks if bike data is available in the cache (i.e., data requested within the last 5 minutes).
    If cached data is available, it returns the data as a list of dictionaries. Otherwise, it fetches new data from
    the bikes API, saves it to the cache, and returns the newly inserted records.

    Returns:
        list or dict: A list of dictionaries containing bike station data if successful,
                      or a dictionary with an error message if the API data cannot be fetched.
    """
    conn = get_sql_engine()
    try:
        five_minutes_ago = datetime.datetime.now() - datetime.timedelta(minutes=5)
        cursor = conn.cursor()
        query = """
        SELECT * FROM FetchedBikesData
        WHERE time_requested >= ?
        ORDER BY time_requested DESC;
        """
        cursor.execute(query, (five_minutes_ago,))
        rows = cursor.fetchall()
    finally:
        conn.close()

    def _to_datetime(value):
        """Helper to convert a value to datetime if it's a string."""
        if isinstance(value, datetime.datetime):
            return value
        try:
            return datetime.datetime.fromisoformat(value)
        except Exception:
            return value  # If conversion fails, return as-is

    if rows:
        print("\n\nUsing cached data\n\n")
        bikes_data = []
        for row in rows:
            # Convert the time_requested and last_update values explicitly to datetime
            time_requested_val = _to_datetime(row[0])
            last_update_val = _to_datetime(row[5])
            bikes_data.append(
                {
                    "time_requested": time_requested_val,
                    "station_id": row[1],
                    "available_bikes": row[2],
                    "available_bike_stands": row[3],
                    "status": row[4],
                    "last_update": last_update_val,
                    "address": row[6],
                    "banking": row[7],
                    "bonus": row[8],
                    "bike_stands": row[9],
                    "name": row[10],
                    "position": {"lat": row[11], "lng": row[12]},
                }
            )
        return bikes_data
    else:
        print("\n\nFetching new data from API\n\n")
        bikes_text = get_data_from_jcdecaux()
        if bikes_text:
            bikes_data = json.loads(bikes_text)
            inserted_records = save_bikes_data_to_cache_db(bikes_data, return_rows=True)
            return inserted_records
        else:
            return {"error": "Unable to fetch bikes data"}

