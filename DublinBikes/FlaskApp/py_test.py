import unittest
from unittest.mock import patch, MagicMock
from flask import json
from DublinBikes.FlaskApp import app

class DublinBikesTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.app = app.test_client()
        cls.app.testing = True

    def test_home_route(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Dublin Bikes', response.data)

    def test_login_route(self):
        response = self.app.get('/login')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Login', response.data)

    def test_register_route(self):
        response = self.app.get('/register')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Register', response.data)

    @patch('DublinBikes.SqlCode.user_db.get_user_by_email')
    def test_successful_login(self, mock_get_user):
        mock_get_user.return_value = {'email': 'test@example.com', 'password': 'hashed_password'}
        with patch('werkzeug.security.check_password_hash', return_value=True):
            response = self.app.post('/login', data={'email': 'test@example.com', 'password': 'password'})
            self.assertEqual(response.status_code, 302)
            self.assertIn('/home', response.headers['Location'])

    @patch('DublinBikes.DataFrontend.data_realtime_weather.get_current_weather_data')
    def test_current_weather_api(self, mock_get_weather):
        mock_get_weather.return_value = {'weather_main': 'Clouds', 'weather_description': 'overcast clouds'}
        response = self.app.get('/api/current_weather')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['weather_main'], 'Clouds')

    @patch('DublinBikes.DataFrontend.data_realtime_bikes.get_current_bikes_data')
    def test_current_bikes_api(self, mock_get_bikes):
        mock_get_bikes.return_value = {'station': 'CLARENDON ROW', 'available_bikes': 10}
        response = self.app.get('/api/current_bikes')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['station'], 'CLARENDON ROW')

if __name__ == '__main__':
    unittest.main()
