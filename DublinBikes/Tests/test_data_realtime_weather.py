import json
import datetime
import pytest
import sqlite3
from DublinBikes.FontEndData import data_realtime_weather
from DublinBikes.SqlCode import sql_utils

@pytest.fixture
def in_memory_db_weather(monkeypatch):
    # Create an in-memory database.
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    # Override get_sql_engine() to return this connection.
    monkeypatch.setattr(sql_utils, "get_sql_engine", lambda: conn)
    # Create the required tables on this connection.
    sql_utils.create_data_base()
    yield conn
    conn.close()

def dummy_get_data_from_openweather(link=None):
    dummy_data = {
        "dt": int(datetime.datetime.now().timestamp()),
        "main": {
            "temp": 15.0,
            "feels_like": 14.0,
            "humidity": 80,
            "pressure": 1013
        },
        "sys": {
            "sunrise": int(datetime.datetime.now().timestamp()),
            "sunset": int(datetime.datetime.now().timestamp())
        },
        "wind": {
            "speed": 5.0,
            "gust": 7.0
        },
        "weather": [{"icon": "01d"}],
        "id": 2964574
    }
    return json.dumps(dummy_data)

@pytest.fixture(autouse=True)
def patch_openweather(monkeypatch):
    monkeypatch.setattr(data_realtime_weather, "get_data_from_openweather", dummy_get_data_from_openweather)

def test_get_current_weather_data(in_memory_db_weather):
    weather = data_realtime_weather.get_current_weather_data()
    assert isinstance(weather, dict)
    assert "temp" in weather

def test_get_forecast_weather_data(in_memory_db_weather):
    forecast = data_realtime_weather.get_forecast_weather_data("hourly", datetime.datetime.now().isoformat())
    assert isinstance(forecast, dict)
