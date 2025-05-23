import os
import sqlite3
from DublinBikes.Utils.params import *

"""
Module: sql_utils
=================

This module provides utility functions for managing the SQLite database connection,
executing SQL commands, and creating the database schema for the Dublin Bikes project.

Functions:
    - get_db_path: Returns the absolute path to the SQLite database file.
    - get_sql_engine: Creates and returns a SQLite connection configured to allow row access by column name.
    - execute_sql: Executes a given SQL command on the provided connection, printing query results or affected row counts.
    - create_data_base: Creates all required tables if they do not already exist.
    - test_queries: Runs sample queries to verify the database setup.

Note:
    Legacy code for AWS RDS (using SQLAlchemy) is retained as comments and is not active.
"""

import logging

logger = logging.getLogger(__name__)




def get_db_path() -> str:
    """
    Get the absolute path to the SQLite database file.

    The database file is expected to reside in the "data" folder at the project root.

    Returns:
        str: The absolute path to the "db.sqlite3" file.
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_folder = os.path.join(base_dir, "data")
    return os.path.join(data_folder, "db.sqlite3")


def get_sql_engine() -> sqlite3.Connection:
    """
    Establish and return a connection to the SQLite database.

    If the database file does not exist, SQLite will automatically create it.
    The connection is set with a row_factory so that rows can be accessed by column name.

    Returns:
        sqlite3.Connection: A connection to the SQLite database.

    Raises:
        sqlite3.Error: If there is an error connecting to the database.
    """
    db_path = get_db_path()
    logger.info("Connecting to database at %s", db_path)

    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("SELECT 1")  # Test the connection.
        logger.info("Database connection established")
    except sqlite3.Error as error:
        logger.error("Failed to connect to database: %s", error)
        raise

    return conn


def execute_sql(sql: str, connection: sqlite3.Connection) -> None:
    """
    Execute a SQL command and print the results or execution status.

    For SELECT queries, this function fetches and prints the returned rows.
    For non-SELECT queries, it prints the total number of rows affected since the connection was opened.

    Parameters:
        sql (str): The SQL command to execute.
        connection (sqlite3.Connection): The active SQLite connection.

    Returns:
        None

    Raises:
        sqlite3.Error: If execution of the SQL command fails.
    """
    try:
        with connection:
            cursor = connection.execute(sql)
            if sql.strip().upper().startswith("SELECT"):
                rows = cursor.fetchall()
                
            else:
                affected = connection.total_changes
                logger.info(f"Query executed successfully. Total rows affected (since connection opened): {affected}")
    except sqlite3.Error as error:
        logger.info(f"Failed to execute query: {error}")
        raise


def create_data_base() -> None:
    """
    Create the necessary tables in the SQLite database.

    This function executes SQL CREATE TABLE statements for the following tables:
      - user
      - station
      - availability
      - current
      - FetchedWeatherData
      - FetchedBikesData

    If a table already exists, it will not be recreated.

    Returns:
        None
    """
    engine = get_sql_engine()

    sql_users_table = """
    CREATE TABLE IF NOT EXISTS user (
        email TEXT PRIMARY KEY,
        username TEXT UNIQUE,
        first_name TEXT,
        last_name TEXT,
        password TEXT,
        default_station INTEGER
    );
    """

    sql_station_table = """
    CREATE TABLE IF NOT EXISTS station (
        station_id INTEGER NOT NULL,
        address VARCHAR(128),
        banking INTEGER,
        bonus INTEGER,
        bike_stands INTEGER,
        name VARCHAR(128),
        position_lat FLOAT,
        position_lng FLOAT,
        PRIMARY KEY (station_id)
    );
    """

    sql_availability_table = """
    CREATE TABLE IF NOT EXISTS availability (
        station_id INTEGER NOT NULL,
        last_update DATETIME NOT NULL,
        available_bikes INTEGER,
        available_bike_stands INTEGER,
        status VARCHAR(128),
        PRIMARY KEY (station_id, last_update)
    );
    """

    sql_current_table = """
    CREATE TABLE IF NOT EXISTS current (
        dt DATETIME NOT NULL,
        feels_like FLOAT,
        humidity INTEGER,
        pressure INTEGER,
        sunrise DATETIME,
        sunset DATETIME,
        temp FLOAT,
        uvi FLOAT,
        weather_id INTEGER,
        wind_gust FLOAT,
        wind_speed FLOAT,
        rain_1h FLOAT,
        snow_1h FLOAT,
        PRIMARY KEY (dt)
    );
    """

    sql_fetched_weather = """    
    CREATE TABLE IF NOT EXISTS FetchedWeatherData (
        timestamp_requested DATETIME NOT NULL,
        timestamp_weatherinfo DATETIME NOT NULL,
        forecast_type TEXT,         
        target_datetime DATETIME,     
        feels_like FLOAT, 
        humidity INTEGER,
        pressure INTEGER,
        sunrise DATETIME,
        sunset DATETIME,
        temp FLOAT,
        uvi FLOAT,
        weather_id INTEGER,
        wind_gust FLOAT,
        wind_speed FLOAT,
        rain_1h FLOAT,
        snow_1h FLOAT,
        PRIMARY KEY (timestamp_requested, timestamp_weatherinfo)
    );
    """

    sql_fetched_bikes = """
    CREATE TABLE IF NOT EXISTS FetchedBikesData (
        time_requested DATETIME NOT NULL,
        station_id INTEGER NOT NULL,
        available_bikes INTEGER,
        available_bike_stands INTEGER,
        status VARCHAR(128),
        last_update DATETIME,
        address VARCHAR(128),
        banking INTEGER,
        bonus INTEGER,
        bike_stands INTEGER,
        name VARCHAR(128),
        position_lat FLOAT,
        position_lng FLOAT,
        PRIMARY KEY (time_requested, station_id)
    );
    """

    execute_sql(sql_users_table, engine)
    execute_sql(sql_station_table, engine)
    execute_sql(sql_availability_table, engine)
    execute_sql(sql_current_table, engine)
    execute_sql(sql_fetched_weather, engine)
    execute_sql(sql_fetched_bikes, engine)



if __name__ == "__main__":
    get_db_path()
    create_data_base()
