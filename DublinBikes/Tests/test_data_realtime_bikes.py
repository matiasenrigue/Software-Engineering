import json
import datetime
import pytest
import sqlite3
from DublinBikes.DataFrontend import data_realtime_bikes
from DublinBikes.SqlCode import sql_utils
from DublinBikes.DataMining.scrapper_jc_decaux import get_data_from_jcdecaux

@pytest.fixture
def in_memory_db(monkeypatch):
    # Create an in-memory database.
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    # Override get_sql_engine() to return this connection.
    monkeypatch.setattr(sql_utils, "get_sql_engine", lambda: conn)
    # Now create the required tables on this connection.
    sql_utils.create_data_base()
    yield conn
    conn.close()

def dummy_get_data_from_jcdecaux():
    dummy_data = [{
        "number": 1,
        "available_bikes": 5,
        "available_bike_stands": 15,
        "status": "OPEN",
        "last_update": int(datetime.datetime.now().timestamp() * 1000),
        "address": "Dummy Addr",
        "banking": 1,
        "bonus": 0,
        "bike_stands": 20,
        "name": "Dummy Station",
        "position": {"lat": 53.350, "lng": -6.260}
    }]
    return json.dumps(dummy_data)

@pytest.fixture(autouse=True)
def patch_get_data(monkeypatch):
    monkeypatch.setattr(data_realtime_bikes, "get_data_from_jcdecaux", dummy_get_data_from_jcdecaux)

def test_get_current_bikes_data(in_memory_db):
    bikes_data = data_realtime_bikes.get_current_bikes_data()
    assert isinstance(bikes_data, list)
    assert bikes_data[0]["name"] == "Dummy Station"
