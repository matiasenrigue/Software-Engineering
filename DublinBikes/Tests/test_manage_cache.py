import os
from datetime import date
import pytest
from DublinBikes.FontEndData import manage_cache
import sqlite3

def test_clean_cache(tmp_path, monkeypatch):
    # Create a temporary "data" folder and a dummy lastcachedelete.txt file.
    data_folder = tmp_path / "data"
    data_folder.mkdir()
    cache_file = data_folder / "lastcachedelete.txt"
    cache_file.write_text("1900-01-01")
    
    # Patch os.path.abspath and os.path.dirname so that the base directory is tmp_path.
    monkeypatch.setattr(os.path, "abspath", lambda path: str(tmp_path))
    monkeypatch.setattr(os.path, "dirname", lambda path: str(tmp_path))
    
    # Patch get_sql_engine to return an in-memory SQLite connection.
    monkeypatch.setattr(manage_cache, "get_sql_engine", lambda: sqlite3.connect(":memory:"))
    
    # Call the clean_cache function.
    manage_cache.clean_cache()
    
    # Now, the cache file should contain today's date.
    today_str = date.today().isoformat()
    content = cache_file.read_text().strip()
    assert content == today_str
