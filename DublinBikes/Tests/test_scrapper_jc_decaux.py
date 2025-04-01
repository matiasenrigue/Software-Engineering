"""
Tests for scrapper_jc_decaux module.
"""

import json
import datetime
import sqlite3
import tempfile
import pytest
from DublinBikes.DataMining import scrapper_jc_decaux
from DublinBikes.SqlCode import sql_utils

class DummyResponse:
    def __init__(self, text):
        self.text = text

def dummy_requests_get(*args, **kwargs):
    dummy_data = json.dumps([{
        "number": 1,
        "address": "Dummy Address",
        "banking": 1,
        "bonus": 0,
        "bike_stands": 20,
        "name": "Dummy Station",
        "position": {"lat": 53.350, "lng": -6.260},
        "available_bikes": 5,
        "available_bike_stands": 15,
        "status": "OPEN",
        "last_update":  int(datetime.datetime.now().timestamp() * 1000)
    }])
    return DummyResponse(dummy_data)

@pytest.fixture(autouse=True)
def patch_requests(monkeypatch):
    monkeypatch.setattr("DublinBikes.DataMining.scrapper_jc_decaux.requests.get", dummy_requests_get)

def dummy_execute_sql(query, engine):
    """
    Dummy SQL executor that simply records the query.
    """
    if not hasattr(engine, "queries"):
        engine.queries = []
    engine.queries.append(query)

@pytest.fixture
def dummy_engine():
    """
    Dummy engine: a simple object to record SQL queries.
    """
    class DummyEngine:
        pass
    return DummyEngine()

def test_get_data_from_jcdecaux():
    """
    Test that get_data_from_jcdecaux returns valid JSON text.
    """
    data = scrapper_jc_decaux.get_data_from_jcdecaux()
    assert data is not None
    parsed = json.loads(data)
    assert isinstance(parsed, list)
    assert parsed[0]["name"] == "Dummy Station"

def test_save_availability_data_to_db(dummy_engine, monkeypatch):
    """
    Test that save_availability_data_to_db calls execute_sql with a valid query.
    """
    monkeypatch.setattr(scrapper_jc_decaux, "execute_sql", dummy_execute_sql)
    dummy_data = json.dumps([{
        "number": 1,
        "available_bikes": 5,
        "available_bike_stands": 15,
        "status": "OPEN",
        "last_update": int(datetime.datetime.now().timestamp() * 1000)
    }])
    scrapper_jc_decaux.save_availability_data_to_db(dummy_data, dummy_engine)
    assert hasattr(dummy_engine, "queries")
    assert len(dummy_engine.queries) >= 1

def test_save_stations_data_to_db(dummy_engine, monkeypatch):
    """
    Test that save_stations_data_to_db builds the expected SQL insert query.
    """
    monkeypatch.setattr(scrapper_jc_decaux, "execute_sql", dummy_execute_sql)
    dummy_data = json.dumps([{
        "number": 1,
        "address": "Dummy Address",
        "banking": 1,
        "bonus": 0,
        "bike_stands": 20,
        "name": "Dummy Station",
        "position": {"lat": 53.350, "lng": -6.260}
    }])
    scrapper_jc_decaux.save_stations_data_to_db(dummy_data, dummy_engine)
    assert hasattr(dummy_engine, "queries")
    query = dummy_engine.queries[-1]
    assert "INSERT INTO station" in query
