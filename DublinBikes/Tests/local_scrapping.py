"""
Tests for the local_scrapping module.
"""

import os
import datetime
import csv
import json
import tempfile

import pytest
from DublinBikes.DataMining import local_scrapping


def test_get_data_folder(tmp_path, monkeypatch):
    """
    Test that get_data_folder returns a valid path and creates the folder if it doesn't exist.
    """
    # Temporarily change the __file__ attribute to point to a temp directory.
    temp_dir = tmp_path / "dummy_project" / "DublinBikes" / "DataMining"
    temp_dir.mkdir(parents=True)
    monkeypatch.setattr(local_scrapping, "__file__", str(temp_dir / "dummy.py"))
    data_folder = local_scrapping.get_data_folder()
    assert os.path.isdir(data_folder), "Data folder should exist after calling get_data_folder()"

def test_create_data_file(tmp_path, monkeypatch):
    """
    Test that create_data_file creates an empty CSV file with a timestamp.
    """
    # Setup a dummy __file__ to control the folder structure.
    dummy_dir = tmp_path / "DublinBikes" / "DataMining"
    dummy_dir.mkdir(parents=True)
    monkeypatch.setattr(local_scrapping, "__file__", str(dummy_dir / "dummy.py"))
    file_path = local_scrapping.create_data_file("testfile")
    assert os.path.isfile(file_path), "Data file should be created."
    # Check that the file is empty.
    assert os.path.getsize(file_path) == 0

def test_save_data_to_file(tmp_path):
    """
    Test save_data_to_file with valid JSON data and with plain text.
    """
    # Prepare a temporary file path.
    file_path = tmp_path / "output.csv"
    # Valid JSON list of dicts.
    data = '[{"col1": "val1", "col2": "val2"}]'
    local_scrapping.save_data_to_file(data, str(file_path))
    # Read CSV file and check headers.
    with open(str(file_path), newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        assert len(rows) == 1
        assert rows[0]["col1"] == "val1"
    
    # Now test with plain text.
    file_path2 = tmp_path / "output2.txt"
    plain_text = "Just some text"
    local_scrapping.save_data_to_file(plain_text, str(file_path2))
    with open(str(file_path2), "r") as f:
        content = f.read()
        assert "Just some text" in content
