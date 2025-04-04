import unittest
from typing import Any, Dict, List
from sqlite3 import Connection
from datetime import datetime
from DublinBikes.DataFrontend.data_realtime_bikes import get_current_bikes_data
from DublinBikes.SqlCode.sql_utils import get_sql_engine


class TestRealtimeBikes(unittest.TestCase):
    """
    Test the retrieval and caching of real-time bikes data from the JCDecaux API.
    This version minimizes API calls by calling get_current_bikes_data() only once in setUp,
    and then uses that cached result for multiple comparisons.
    """

    def setUp(self) -> None:
        """
        Clear the FetchedBikesData table and retrieve the bikes data once for use in subsequent tests.
        """
        conn: Connection = get_sql_engine()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM FetchedBikesData;")
            conn.commit()
        finally:
            conn.close()
            
        # Call the function once and store the result
        # It will be API data, as the cache is cleared.
        self.API_data: List[Dict[str, Any]] = get_current_bikes_data()


    def tearDown(self) -> None:
        """
        Clear the FetchedBikesData table after each test.
        """
        conn: Connection = get_sql_engine()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM FetchedBikesData;")
            conn.commit()
        finally:
            conn.close()


    def test_cached_data_consistency(self) -> None:
        """
        Verify that two consecutive calls to get_current_bikes_data return identical data.
        """
        # First call was already made in setUp.
        first_call = self.API_data
        # Make a second call.
        second_call = get_current_bikes_data()
        
        # Sort the data for consistent comparison
        first_call_sorted = sorted(first_call, key=lambda x: x["station_id"])
        second_call_sorted = sorted(second_call, key=lambda x: x["station_id"])
                
        self.assertEqual(first_call_sorted, second_call_sorted, "Both calls should return identical cached bikes data.")
        

    def test_length_consistency(self) -> None:
        """
        Instead of checking against a fixed number, verify that the length of the bikes data is the same
        between the API call result (from setUp) and a cached call.
        """
        length_API = len(self.API_data)
        length_second = len(get_current_bikes_data())
        self.assertEqual(length_API, length_second, "Both calls should return the same number of station records.")
        


    def test_station_record_fields(self) -> None:
        """
        Verify that each station record contains all expected keys and that the 'position' field is a dict.
        """
        expected_keys = {
            "time_requested", "station_id", "available_bikes", "available_bike_stands",
            "status", "last_update", "address", "banking", "bonus", "bike_stands", "name", "position"
        }
        for station in self.API_data:
            self.assertTrue(expected_keys.issubset(station.keys()),
                            f"Station record missing expected keys. Found: {station.keys()}")
            self.assertIsInstance(station["position"], dict, "The 'position' field should be a dict.")
            self.assertIn("lat", station["position"], "The 'position' dict should include 'lat'.")
            self.assertIn("lng", station["position"], "The 'position' dict should include 'lng'.")



    def test_time_requested_format(self) -> None:
        """
        Verify that the 'time_requested' field in at least one station record is a valid datetime.
        If the value is a string, attempt to parse it; if it is already a datetime object, consider it valid.
        """
        time_value = self.API_data[0].get("time_requested")
        if isinstance(time_value, str):
            try:
                datetime.strptime(time_value, "%Y-%m-%d %H:%M:%S.%f")
            except Exception as e:
                self.fail(f"'time_requested' string is not in a valid datetime format: {e}")
        elif not isinstance(time_value, datetime):
            self.fail(f"'time_requested' field is neither a string nor a datetime object: {type(time_value)}")


if __name__ == '__main__':
    unittest.main()
