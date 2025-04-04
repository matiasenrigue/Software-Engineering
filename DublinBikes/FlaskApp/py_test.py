import unittest
from flask import Flask, jsonify, session
from DublinBikes.FlaskApp import app
from unittest.mock import patch

class FlaskAppTestCase(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.client.testing = True

    def test_home_page(self):
        """Test the home page route."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'DUBLIN BIKES', response.data)

    @patch('DublinBikes.DataFrontend.data_realtime_weather.get_current_weather_data')
    def test_current_weather_api(self, mock_weather):
        """Test the current weather API endpoint."""
        mock_weather.return_value = {'weather': 'Cloudy', 'temp': 280}
        response = self.client.get('/api/current_weather')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Cloudy', response.data)

    @patch('DublinBikes.DataFrontend.data_realtime_bikes.get_current_bikes_data')
    def test_current_bikes_api(self, mock_bikes):
        """Test the current bikes API endpoint."""
        mock_bikes.return_value = {'station_id': 10, 'bikes_available': 5}
        response = self.client.get('/api/current_bikes')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'"bikes_available": 5', response.data)

    @patch('DublinBikes.DataFrontend.data_realtime_weather.get_forecast_weather_data')
    def test_forecast_weather_api(self, mock_forecast):
        """Test the forecast weather API endpoint."""
        mock_forecast.return_value = {'forecast': 'Rainy'}
        response = self.client.get('/api/forecast_weather?target_datetime=2025-04-05T10:00')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Rainy', response.data)

    def test_login(self):
        """Test the login functionality."""
        with app.test_client() as client:
            response = client.post('/login', data={'email': 'user@example.com', 'password': 'password'})
            self.assertIn(b'Error: Invalid email or password.', response.data)

if __name__ == '__main__':
    unittest.main()

