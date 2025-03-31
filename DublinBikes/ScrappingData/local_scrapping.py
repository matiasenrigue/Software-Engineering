import os
import datetime
import json
import csv


def get_data_folder() -> str:
    """
    Ensure that the data folder exists and return the path to it.
    If it does not exist, create it.
    """

    data_folder: str = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data"
    )

    if not os.path.exists(data_folder):
        os.mkdir(data_folder)
        print("Folder 'data' created!")

    return data_folder


def create_data_file(filename: str) -> os.path:
    """
    Function to save the data to a text file.
    """

    data_folder: str = get_data_folder()
    time_stamp: str = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    text_file: str = os.path.join(data_folder, f"{filename}_{time_stamp}.csv")

    # create file, only create, not write anything
    with open(text_file, "w") as f:
        pass

    return text_file


def save_data_to_file(data: str, filepath: os.path) -> None:
    """
    Function to save the data to a text file.
    """
    if not os.path.exists(filepath):
        with open(filepath, "w") as f:
            f.write(data)

    else:
        with open(filepath, "a") as f:
            f.write(data)


def save_data_to_file(data: str, filepath: str) -> None:
    """
    Save data to a CSV file. If the data is in JSON format, convert it to CSV.
    Makes sure to write the headers only the first time the file is written to.
    """
    try:
        # Try to parse the data as JSON
        json_data = json.loads(data)

        # Checks if file is empty
        file_empty = True
        if os.path.exists(filepath):
            if os.stat(filepath).st_size > 0:
                file_empty = False

        # If it is a list of dictionaries (e.g. bikes data)
        if isinstance(json_data, list) and json_data and isinstance(json_data[0], dict):
            with open(filepath, "a", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=json_data[0].keys())
                if file_empty:
                    writer.writeheader()
                writer.writerows(json_data)

        # If it is a single dictionary (e.g. weather data)
        elif isinstance(json_data, dict):
            with open(filepath, "a", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=json_data.keys())
                if file_empty:
                    writer.writeheader()
                writer.writerow(json_data)
        else:
            # If JSON data is not in an expected format, write the raw data.
            with open(filepath, "a") as f:
                f.write(data)

    except Exception as e:
        # If parsing as JSON fails, simply write the raw data.
        with open(filepath, "a") as f:
            f.write(data)
