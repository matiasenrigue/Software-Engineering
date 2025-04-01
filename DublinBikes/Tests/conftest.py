"""
Conftest for pytest.
Provides fixtures for a temporary SQLite database and a Flask test client.
"""

import sqlite3
import pytest
from pathlib import Path
from DublinBikes.SqlCode import sql_utils
from DublinBikes.FlaskApp import app

@pytest.fixture
def temp_db(tmp_path, monkeypatch):
    """
    Create a temporary SQLite database file and patch get_db_path.
    """
    db_file = tmp_path / "test_db.sqlite3"
    monkeypatch.setattr(sql_utils, "get_db_path", lambda: str(db_file))
    
    # Create a connection to initialize tables if needed.
    conn = sqlite3.connect(str(db_file))
    conn.row_factory = sqlite3.Row
    yield conn
    conn.close()


@pytest.fixture
def flask_client():
    """
    Create a test client for the Flask application.
    """
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client
