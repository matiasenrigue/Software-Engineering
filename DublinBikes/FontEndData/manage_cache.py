import os
from datetime import date
from DublinBikes.SQL_code.sql_utils import get_sql_engine


def clean_cache():
    """
    Cleans the cache by deleting records from the database that are older than today.
    It also updates a cache file to indicate the last time the cache was cleaned.

    Executed withing the Weather API code, as its less frequent than the bike data.
    """

    # Determine the data folder
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_folder = os.path.join(base_dir, "data")
    cache_file = os.path.join(data_folder, "lastcachedelete.txt")

    # Use ISO date string (YYYY-MM-DD)
    today_str = date.today().isoformat()

    # Check if the file exists and if cache was already cleaned today
    if os.path.exists(cache_file):
        with open(cache_file, "r") as f:
            last_deleted = f.read().strip()
        if last_deleted == today_str:
            print("Cache already cleaned today. No action taken.")
            return

    # Connect to the SQLite database
    conn = get_sql_engine()
    try:
        cursor = conn.cursor()
        # Delete records from FetchedWeatherData where the date is before today.
        delete_weather = (
            "DELETE FROM FetchedWeatherData WHERE date(timestamp_requested) < ?;"
        )
        cursor.execute(delete_weather, (today_str,))

        # Delete records from FetchedBikesData where the date is before today.
        delete_bikes = "DELETE FROM FetchedBikesData WHERE date(time_requested) < ?;"
        cursor.execute(delete_bikes, (today_str,))

        conn.commit()
        print("Cache cleaned successfully.")
    except Exception as e:
        print("Error cleaning cache:", e)
    finally:
        conn.close()

    # Update (or create) the cache file with today's date.
    with open(cache_file, "w") as f:
        f.write(today_str)


if __name__ == "__main__":
    clean_cache()
