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
    print("🌐 Connecting to the database file:", db_path)

    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("SELECT 1")  # Test the connection.
        print("✅ Connection to the SQLite database established successfully.")
    except sqlite3.Error as error:
        print(f"Failed to establish connection to the SQLite database: {error}")
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
            print(f"Executing the following SQL command: {sql}")
            cursor = connection.execute(sql)
            if sql.strip().upper().startswith("SELECT"):
                rows = cursor.fetchall()
                if rows:
                    print("Query returned the following rows:")
                    for row in rows:
                        print(dict(row))
                else:
                    print("Query returned no rows.")
            else:
                affected = connection.total_changes
                print(f"Query executed successfully. Total rows affected (since connection opened): {affected}")
    except sqlite3.Error as error:
        print(f"Failed to execute query: {error}")
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


def test_queries() -> None:
    """
    Run test queries to verify the database setup.

    This function executes several SQL queries:
      - Counts the total number of rows in the "station" table.
      - Retrieves rows for the station with address "Smithfield North".
      - Executes additional queries on the "availability" and "current" tables.

    Returns:
        None
    """
    engine = get_sql_engine()

    sql = "select count(*) from station;"
    execute_sql(sql, engine)

    sql = "select * from station where address = 'Smithfield North';"
    execute_sql(sql, engine)

    execute_sql("select * from station where address = 'Smithfield North';", engine)
    execute_sql("select * from availability where available_bike_stands > 20 LIMIT 5", engine)
    execute_sql("select * from current where temp > 20", engine)


if __name__ == "__main__":
    get_db_path()
    create_data_base()
    test_queries()
