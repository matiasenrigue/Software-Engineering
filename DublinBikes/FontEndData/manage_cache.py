import os
from datetime import date
from DublinBikes.SQL_code.sql_utils import get_sql_engine

"""
Module: manage_cache
----------------------
This module provides functionality to clean the cache database.
It removes outdated records from both weather and bike data tables and updates a cache file
to record the last time the cache was cleaned.
"""


def clean_cache():
    """
    Clean the cache database by removing outdated records.

    This function deletes records from the 'FetchedWeatherData' and 'FetchedBikesData' tables
    that were requested before the current day. It also updates a cache file 'lastcachedelete.txt'
    to indicate the last cleaning date. If the cache has already been cleaned today, no action is taken.
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_folder = os.path.join(base_dir, "data")
    cache_file = os.path.join(data_folder, "lastcachedelete.txt")
    today_str = date.today().isoformat()
    if os.path.exists(cache_file):
        with open(cache_file, "r") as f:
            last_deleted = f.read().strip()
        if last_deleted == today_str:
            print("Cache already cleaned today. No action taken.")
            return
    conn = get_sql_engine()
    try:
        cursor = conn.cursor()
        delete_weather = (
            "DELETE FROM FetchedWeatherData WHERE date(timestamp_requested) < ?;"
        )
        cursor.execute(delete_weather, (today_str,))
        delete_bikes = "DELETE FROM FetchedBikesData WHERE date(time_requested) < ?;"
        cursor.execute(delete_bikes, (today_str,))
        conn.commit()
        print("Cache cleaned successfully.")
    except Exception as e:
        print("Error cleaning cache:", e)
    finally:
        conn.close()
    with open(cache_file, "w") as f:
        f.write(today_str)


if __name__ == "__main__":
    clean_cache()
