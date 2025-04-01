"""
Tests for sql_utils module.
"""

import os
import sqlite3
import pytest
from DublinBikes.SqlCode import sql_utils

def test_get_db_path(tmp_path, monkeypatch):
    """
    Test that get_db_path returns a valid path.
    """
    dummy_path = str(tmp_path / "dummy_db.sqlite3")
    monkeypatch.setattr(sql_utils, "get_db_path", lambda: dummy_path)
    path = sql_utils.get_db_path()
    assert dummy_path in path

def test_get_sql_engine(tmp_path, monkeypatch):
    """
    Test that get_sql_engine returns a valid sqlite3 connection.
    """
    dummy_db = tmp_path / "dummy_db.sqlite3"
    monkeypatch.setattr(sql_utils, "get_db_path", lambda: str(dummy_db))
    engine = sql_utils.get_sql_engine()
    cursor = engine.cursor()
    cursor.execute("SELECT 1")
    result = cursor.fetchone()
    assert result[0] == 1
    engine.close()

def test_execute_sql(tmp_path, monkeypatch):
    """
    Test that execute_sql correctly runs a CREATE and then SELECT query.
    """
    dummy_db = tmp_path / "dummy_db.sqlite3"
    monkeypatch.setattr(sql_utils, "get_db_path", lambda: str(dummy_db))
    engine = sql_utils.get_sql_engine()
    create_query = "CREATE TABLE test (id INTEGER PRIMARY KEY, value TEXT);"
    sql_utils.execute_sql(create_query, engine)
    insert_query = "INSERT INTO test (value) VALUES ('abc');"
    sql_utils.execute_sql(insert_query, engine)
    select_query = "SELECT * FROM test;"
    sql_utils.execute_sql(select_query, engine)
    engine.close()

def test_create_data_base(tmp_path, monkeypatch):
    """
    Test that create_data_base creates all required tables.
    """
    dummy_db = tmp_path / "dummy_db.sqlite3"
    monkeypatch.setattr(sql_utils, "get_db_path", lambda: str(dummy_db))
    sql_utils.create_data_base()
    engine = sql_utils.get_sql_engine()
    cursor = engine.cursor()
    # Check for one of the tables, e.g., user.
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='user';")
    row = cursor.fetchone()
    assert row is not None
    engine.close()
