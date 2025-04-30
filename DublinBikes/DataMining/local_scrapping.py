import os
import datetime
import json
import csv

"""
Module: local_scrapping
-----------------------
This module provides utility functions for local data storage operations.
It is used by the scrapers to save scraped data to CSV files as a backup or for historical record creation.
Functions include ensuring the existence of the data folder, creating a new timestamped data file,
and saving data (either as raw text or as CSV) to a file.
"""

import logging

logger = logging.getLogger(__name__)


def get_data_folder() -> str:
    """
    Ensure the existence of the data folder and return its path.

    If the data folder does not exist, it will be created.

    Returns:
        str: The absolute path to the data folder.
    """
    data_folder: str = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data"
    )
    if not os.path.exists(data_folder):
        os.mkdir(data_folder)
        logger.info("Folder 'data' created!")
    return data_folder


def create_data_file(filename: str) -> os.path:
    """
    Create a new data file with a timestamped filename.

    This function generates a file path in the data folder with the given filename and a timestamp.
    The file is created (empty) and its path is returned.

    Parameters:
        filename (str): The base name for the file (e.g., "bikes" or "weather").

    Returns:
        str: The absolute path to the newly created file.
    """
    data_folder: str = get_data_folder()
    time_stamp: str = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    text_file: str = os.path.join(data_folder, f"{filename}_{time_stamp}.csv")
    with open(text_file, "w") as f:
        pass
    return text_file


def save_data_to_file(data: str, filepath: str) -> None:
    """
    Save data to a CSV file.

    If the provided data is in JSON format, it will be converted to CSV.
    The function ensures that headers are written only once when the file is empty.
    If the file already exists, data will be appended.

    Parameters:
        data (str): The data to be saved, expected in JSON format.
        filepath (str): The path to the file where the data should be saved.

    Returns:
        None
    """
    try:
        json_data = json.loads(data)
        file_empty = True
        if os.path.exists(filepath) and os.stat(filepath).st_size > 0:
            file_empty = False

        if isinstance(json_data, list) and json_data and isinstance(json_data[0], dict):
            with open(filepath, "a", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=json_data[0].keys())
                if file_empty:
                    writer.writeheader()
                writer.writerows(json_data)
                
        elif isinstance(json_data, dict):
            with open(filepath, "a", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=json_data.keys())
                if file_empty:
                    writer.writeheader()
                writer.writerow(json_data)
        else:
            with open(filepath, "a") as f:
                f.write(data)
                
    except Exception as e:
        with open(filepath, "a") as f:
            f.write(data)
