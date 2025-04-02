"""
Tests for data_loader_SQL module.
"""

import sqlite3
import pytest
from DublinBikes.DataFrontend import data_loader_SQL
from DublinBikes.SqlCode import sql_utils

def test_get_all_stations_data_SQL(tmp_path, monkeypatch):
    """
    Test that get_all_stations_data_SQL returns a list of stations.
    """
    db_file = tmp_path / "test_db.sqlite3"
    monkeypatch.setattr(sql_utils, "get_db_path", lambda: str(db_file))
    conn = sqlite3.connect(str(db_file))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE station (
        station_id INTEGER PRIMARY KEY,
        address TEXT,
        banking INTEGER,
        bonus INTEGER,
        bike_stands INTEGER,
        name TEXT,
        position_lat FLOAT,
        position_lng FLOAT
    );
    """)
    cursor.execute("""
    INSERT INTO station (station_id, address, banking, bonus, bike_stands, name, position_lat, position_lng)
    VALUES (1, 'Test Addr', 1, 0, 20, 'Station A', 53.350, -6.260);
    """)
    conn.commit()
    stations = data_loader_SQL.get_all_stations_data_SQL()
    assert isinstance(stations, list)
    assert stations[0]["name"] == "Station A"
    conn.close()
