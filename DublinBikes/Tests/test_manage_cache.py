import os
import unittest
from datetime import date, timedelta
from sqlite3 import Connection
from DublinBikes.DataFrontend.manage_cache import clean_cache
from DublinBikes.SqlCode.sql_utils import get_sql_engine


class TestManageCache(unittest.TestCase):
    """
    Test the cache cleaning functionality.
    """



    def setUp(self) -> None:
        """
        Remove any existing cache file and insert dummy records in the cache tables.
        """
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.data_folder = os.path.join(base_dir, "data")
        self.cache_file = os.path.join(self.data_folder, "lastcachedelete.txt")

        if os.path.exists(self.cache_file):
            os.remove(self.cache_file)

        # Insert dummy records with yesterday's timestamp into both cache tables.
        conn: Connection = get_sql_engine()
        try:
            cursor = conn.cursor()
            yesterday_str = (date.today() - timedelta(days=1)).isoformat() + " 00:00:00"
            # Dummy record for FetchedWeatherData.
            dummy_weather = (
                yesterday_str,  # timestamp_requested
                yesterday_str,  # timestamp_weatherinfo
                "current",      # forecast_type
                yesterday_str,  # target_datetime
                0, 0, 0, None, None, 0, None, 0, None, 0, None, None,
            )
            cursor.execute(
                """INSERT INTO FetchedWeatherData (
                        timestamp_requested, timestamp_weatherinfo, forecast_type, target_datetime,
                        feels_like, humidity, pressure, sunrise, sunset, temp, uvi, weather_id,
                        wind_gust, wind_speed, rain_1h, snow_1h
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);""",
                dummy_weather
            )
            # Dummy record for FetchedBikesData.
            dummy_bikes = (
                yesterday_str, 1, 0, 0, "OPEN", yesterday_str, "dummy", 0, 0, 0, "dummy", 0.0, 0.0
            )
            cursor.execute(
                """INSERT INTO FetchedBikesData (
                        time_requested, station_id, available_bikes, available_bike_stands,
                        status, last_update, address, banking, bonus, bike_stands, name,
                        position_lat, position_lng
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);""",
                dummy_bikes
            )
            conn.commit()
        finally:
            conn.close()



    def tearDown(self) -> None:
        """
        Clean up the dummy records and remove the cache file.
        """
        conn: Connection = get_sql_engine()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM FetchedWeatherData;")
            cursor.execute("DELETE FROM FetchedBikesData;")
            conn.commit()
        finally:
            conn.close()

        if os.path.exists(self.cache_file):
            os.remove(self.cache_file)



    def test_cache_tables_empty_after_cleaning(self) -> None:
        """
        Test that after calling clean_cache with a future date, both cache tables are empty.
        """
        tomorrow = date.today() + timedelta(days=1)
        clean_cache(tomorrow)

        conn: Connection = get_sql_engine()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM FetchedWeatherData;")
            count_weather = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM FetchedBikesData;")
            count_bikes = cursor.fetchone()[0]
        finally:
            conn.close()

        self.assertEqual(count_weather, 0, "FetchedWeatherData should be empty after cleaning.")
        self.assertEqual(count_bikes, 0, "FetchedBikesData should be empty after cleaning.")



    def test_cache_file_updated(self) -> None:
        """
        Test that after cleaning the cache, the cache file is created and contains today's date.
        """
        tomorrow = date.today() + timedelta(days=1)
        clean_cache(tomorrow)
        with open(self.cache_file, "r") as f:
            content = f.read().strip()
        self.assertEqual(content, date.today().isoformat(), "Cache file should contain today's date.")



    def test_no_action_if_clean_called_twice(self) -> None:
        """
        Test that calling clean_cache again on the same day returns 0 (indicating no action).
        """
        tomorrow = date.today() + timedelta(days=1)
        clean_cache(tomorrow)
        result_second = clean_cache()
        self.assertEqual(result_second, 0, "Clean cache called twice on same day should return 0.")


if __name__ == '__main__':
    unittest.main()
