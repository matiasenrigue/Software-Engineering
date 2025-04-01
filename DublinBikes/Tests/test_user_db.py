"""
Tests for user_db module.
"""

import sqlite3
import pytest
from DublinBikes.SqlCode import user_db, sql_utils

@pytest.fixture
def init_db(tmp_path, monkeypatch):
    """
    Initialize a temporary database with the required schema.
    """
    db_file = tmp_path / "test_user_db.sqlite3"
    monkeypatch.setattr(sql_utils, "get_db_path", lambda: str(db_file))
    sql_utils.create_data_base()
    yield
    # Cleanup is handled by tmp_path

def test_register_and_get_user(init_db):
    """
    Test that a user can be registered and then retrieved.
    """
    email = "test@example.com"
    result = user_db.register_user(email, "testuser", "Test", "User", "secret", 1)
    assert result is True
    user = user_db.get_user_by_email(email)
    assert user is not None
    assert user["username"] == "testuser"

def test_update_user_profile(init_db):
    """
    Test that updating a user profile works correctly.
    """
    email = "update@example.com"
    user_db.register_user(email, "olduser", "Old", "Name", "oldpass", 1)
    result = user_db.update_user_profile(email, "newuser", "New", "Name", "newpass", 2)
    assert result is True
    user = user_db.get_user_by_email(email)
    assert user["username"] == "newuser"
    assert user["default_station"] == 2
