import os
from datetime import date
from DublinBikes.SqlCode.sql_utils import get_sql_engine

"""
Module: manage_cache
----------------------
This module provides functionality to clean the cache database.
It removes outdated records from both weather and bike data tables and updates a cache file
to record the last time the cache was cleaned.
"""

import logging

logger = logging.getLogger(__name__)


def clean_cache(date_today: date = None):
    """
    Clean the cache database by removing outdated records.

    This function deletes records from the 'FetchedWeatherData' and 'FetchedBikesData' tables
    that were requested before the current day. It also updates a cache file 'lastcachedelete.txt'
    to indicate the last cleaning date. If the cache has already been cleaned today, no action is taken.
    
    :param date_today: Optional; if provided, this date will be used instead of today's date.
         To be used for testing purposes: putting tomorrow's date will not delete also the data of today.
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_folder = os.path.join(base_dir, "data")
    cache_file = os.path.join(data_folder, "lastcachedelete.txt")
    
    if not date_today:
        today_str = date.today().isoformat()
    else:
        today_str = date_today.isoformat()
        
    if os.path.exists(cache_file):
        with open(cache_file, "r") as f:
            last_deleted = f.read().strip()
        if last_deleted == today_str:
            logger.info("Cache already cleaned today. No action taken.")
            return 0
        
    conn = get_sql_engine()
    try:
        cursor = conn.cursor()
        
        delete_weather = ("DELETE FROM FetchedWeatherData WHERE date(timestamp_requested) < ?;")
        cursor.execute(delete_weather, (today_str,))
        
        delete_bikes = "DELETE FROM FetchedBikesData WHERE date(time_requested) < ?;"
        cursor.execute(delete_bikes, (today_str,))
        
        conn.commit()
        logger.info("Cache cleaned successfully.")
        
    except Exception as e:
        logger.info("Error cleaning cache:", e)
    finally:
        conn.close()
    with open(cache_file, "w") as f:
        f.write(date.today().isoformat())


if __name__ == "__main__":
    clean_cache()
