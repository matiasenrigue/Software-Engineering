"""
Tests for scrapper_open_weather module.
"""

import json
import datetime
import pytest
from DublinBikes.DataMining import scrapper_open_weather

class DummyResponse:
    def __init__(self, text):
        self.text = text
    def raise_for_status(self):
        pass

def dummy_requests_get(*args, **kwargs):
    dummy_data = json.dumps({
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
        "id": 2964574
    })
    return DummyResponse(dummy_data)

@pytest.fixture(autouse=True)
def patch_requests(monkeypatch):
    monkeypatch.setattr("DublinBikes.DataMining.scrapper_open_weather.requests.get", dummy_requests_get)

def dummy_execute_sql(query, engine):
    if not hasattr(engine, "queries"):
        engine.queries = []
    engine.queries.append(query)

@pytest.fixture
def dummy_engine():
    class DummyEngine:
        pass
    return DummyEngine()

def test_get_data_from_openweather():
    data = scrapper_open_weather.get_data_from_openweather()
    assert data is not None
    parsed = json.loads(data)
    assert "main" in parsed
    assert parsed["main"]["temp"] == 15.0

def test_save_current_data_to_db(dummy_engine, monkeypatch):
    monkeypatch.setattr(scrapper_open_weather, "execute_sql", dummy_execute_sql)
    dummy_data = json.dumps({
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
        "id": 2964574
    })
    scrapper_open_weather.save_current_data_to_db(dummy_data, dummy_engine)
    assert hasattr(dummy_engine, "queries")
    assert len(dummy_engine.queries) >= 1
