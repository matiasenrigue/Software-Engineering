import unittest
from datetime import datetime, timedelta
from typing import Any, Dict
from DublinBikes.DataFrontend.data_realtime_weather import get_forecast_weather_data
from DublinBikes.SqlCode.sql_utils import get_sql_engine


class TestForecastWeather(unittest.TestCase):
    """
    Test the retrieval and caching of forecast weather data from the OpenWeather API.
    """

    
    
    def _remove_time_diff(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Remove the 'time_diff' key from the forecast data dictionary if present.

        Args:
            data (Dict[str, Any]): The forecast data dictionary.

        Returns:
            Dict[str, Any]: A copy of the dictionary without the 'time_diff' key.
        """
        data_copy = data.copy()
        data_copy.pop("time_diff", None)
        return data_copy

    
    
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
        target_dt = datetime.now() + timedelta(hours=2)
        target_dt_iso: str = target_dt.isoformat()
        self.API_data: Dict[str, Any] = get_forecast_weather_data("hourly", target_dt_iso)

    
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
        Verify that get_forecast_weather_data returns a dictionary.
        """
        target_dt = datetime.now() + timedelta(hours=2)
        target_dt_iso: str = target_dt.isoformat()
        result: Dict[str, Any] = get_forecast_weather_data("hourly", target_dt_iso)
        self.assertIsInstance(result, dict, "Forecast weather data should be returned as a dict.")

    
    
    def test_data_contains_temperature(self) -> None:
        """
        Verify that the forecast data contains the temperature information.
        """
        target_dt = datetime.now() + timedelta(hours=2)
        target_dt_iso: str = target_dt.isoformat()
        result: Dict[str, Any] = get_forecast_weather_data("hourly", target_dt_iso)
        self.assertIn("temp", result, "Forecast data should contain 'temp' key.")

    
    
    def test_cached_forecast_data_consistency(self) -> None:
        """
        Verify that two consecutive calls with the same target datetime return identical forecast data,
        ignoring the extra 'time_diff' key.
        """
        # API data was already fetched in setUp.
        first_call = self.API_data
        
        # Make a second call --> this will be cached data.
        second_call = get_forecast_weather_data("hourly", first_call["target_datetime"])
        

        # Remove the extra 'time_diff' key before comparison.
        result1_clean = self._remove_time_diff(first_call)
        result2_clean = self._remove_time_diff(second_call)

        self.assertEqual(
            result1_clean, result2_clean,
            "Both calls should return the same cached forecast data (ignoring 'time_diff')."
        )


if __name__ == '__main__':
    unittest.main()
