import unittest
from typing import Any, Dict
from DublinBikes.DataFrontend.data_realtime_weather import get_current_weather_data
from DublinBikes.SqlCode.sql_utils import get_sql_engine


class TestCurrentWeather(unittest.TestCase):
    """
    Test the retrieval and caching of current weather data from the OpenWeather API.
    """


    def setUp(self) -> None:
        """
        Clear the FetchedWeatherData table before each test.
        """
        conn = get_sql_engine()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM FetchedWeatherData;")
            conn.commit()
        finally:
            conn.close()
        
        # Call the function once and store the result
        # It will be API data, as the cache is cleared.
        self.API_data: Dict[str, Any] = get_current_weather_data()



    def tearDown(self) -> None:
        """
        Clear the FetchedWeatherData table after each test.
        """
        conn = get_sql_engine()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM FetchedWeatherData;")
            conn.commit()
        finally:
            conn.close()



    def test_return_type_is_dict(self) -> None:
        """
        Verify that get_current_weather_data returns a dictionary.
        """
        result: Dict[str, Any] = get_current_weather_data()
        self.assertIsInstance(result, dict, "Current weather data should be a dict.")



    def test_data_contains_temperature(self) -> None:
        """
        Verify that the returned weather data contains the temperature information.
        """
        result: Dict[str, Any] = get_current_weather_data()
        self.assertIn("temp", result, "Returned weather data must contain 'temp' key.")



    def test_cached_weather_data_consistency(self) -> None:
        """
        Verify that two consecutive calls to get_current_weather_data within 15 minutes return identical data.
        """
        result1: Dict[str, Any] = self.API_data # Data from API call in setUp
        result2: Dict[str, Any] = get_current_weather_data() # Data from cache
        self.assertEqual(result1, result2, "Both calls should return identical cached weather data.")


if __name__ == '__main__':
    unittest.main()
