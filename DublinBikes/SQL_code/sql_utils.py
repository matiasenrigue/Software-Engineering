from DublinBikes.Utils.params import *
import sqlite3
import os

# We don't need to import the following libraries as we are not using AWS RDS

# from sqlalchemy import create_engine, text
# import sqlalchemy as sqla
# from sqlalchemy.exc import SQLAlchemyError


def get_db_path():

    # Get the path to the database
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_folder = os.path.join(base_dir, "data")
    return os.path.join(data_folder, "db.sqlite3")


def get_sql_engine() -> sqlite3.Connection:
    """
    Function to get the SQLite connection.

    If the file does not exist, sqlite3 will automatically create it.
    Returns a connection with a row_factory set so that rows can be accessed by column name.
    """
    # Define the file path for the SQLite database file (e.g., in the project root)
    db_path = get_db_path()
    print("🌐 Connecting to the database file:", db_path)

    try:
        # This will create the file if it does not exist.
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        # Execute a trivial query to test the connection
        conn.execute("SELECT 1")
        print("✅ Connection to the SQLite database established successfully.")
    except sqlite3.Error as error:
        print(f"Failed to establish connection to the SQLite database: {error}")
        raise

    return conn


def execute_sql(sql: str, connection: sqlite3.Connection) -> None:
    """
    Execute a SQL command and provide feedback.

    For SELECT queries, prints the returned rows.
    For non-SELECT queries, prints the number of rows affected.
    """
    try:
        # Using the connection as a context manager automatically commits or rolls back
        with connection:
            print(f"Executing the following SQL command: {sql}")
            cursor = connection.execute(sql)

            # If the query starts with SELECT, fetch and print the results
            if sql.strip().upper().startswith("SELECT"):
                rows = cursor.fetchall()
                if rows:
                    print("Query returned the following rows:")
                    for row in rows:
                        # Convert each row (sqlite3.Row) to a dict for nicer printing
                        print(dict(row))
                else:
                    print("Query returned no rows.")
            else:
                # For non-SELECT queries, report the number of rows affected.
                affected = connection.total_changes
                print(
                    f"Query executed successfully. Total rows affected (since connection opened): {affected}"
                )
    except sqlite3.Error as error:
        print(f"Failed to execute query: {error}")


##########################################################################################
# The following functions are used to create the tables in the database
##########################################################################################


def create_data_base():
    engine = get_sql_engine()

    # Users table
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

    # Station table
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

    # Availability table
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

    # Current weather table
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

    # forecast_type -- 'current', 'hourly', or 'daily'
    # target_datetime -- The forecast valid time (for current data, same as timestamp_weatherinfo)
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

    # Bikes data cache table
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

    # Execute all the CREATE TABLE statements
    execute_sql(sql_users_table, engine)
    execute_sql(sql_station_table, engine)
    execute_sql(sql_availability_table, engine)
    execute_sql(sql_current_table, engine)
    execute_sql(sql_fetched_weather, engine)
    execute_sql(sql_fetched_bikes, engine)


def test_queries():
    """
    Queries to test that the database is working correctly.
    """
    engine = get_sql_engine()

    # QUERY 1 counts the total number of rows in the station table (count is count, and * is 'all')
    sql = "select count(*) from station;"
    execute_sql(sql, engine)

    # QUERY 2 select the rows associated with station Smithfield North
    sql = "select * from station where address = 'Smithfield North';"
    execute_sql(sql, engine)

    # QUERY 3: Check that the table was correctly updated
    execute_sql("select * from station where address = 'Smithfield North';", engine)
    execute_sql(
        "select * from availability where available_bike_stands > 20 LIMIT 5", engine
    )
    execute_sql("select * from current where temp > 20", engine)


# def drop_fetched_weather_table():
#     engine = get_sql_engine()
#     try:
#         drop_query = "DROP TABLE IF EXISTS FetchedWeatherData;"
#         execute_sql(drop_query, engine)
#         print("FetchedWeatherData table dropped successfully.")
#     finally:
#         engine.close()


if __name__ == "__main__":

    get_db_path()
    create_data_base()
    test_queries()


####### OLD CODE #######
##### IT WILL NOT BE USED AS WE WON'T BE USING AWS RDS #####
#### IT WAS SUBSTITUTED BY THE SQLITE DATABASE ####

# def get_sql_engine() -> sqla.engine.base.Connection:
#     """
#     Function to get the engine to be used to connect to the database.

#     :return: the engine to be used to connect to the database
#     """

#     # If local is True, the connection is made to the local database
#     # If local is False, the connection is made to the remote database
#     local: bool = LOCAL_RUNNING

#     print("🌐 Connecting to the database")

#     if local:
#         connection_string = f"mysql+mysqlconnector://{LOCAL_USER}:{LOCAL_PASSWORD}@{LOCAL_URI}:{PORT}/{LOCAL_DB}"
#         engine = create_engine(connection_string)
#     else:
#         connection_string = f"mysql+mysqlconnector://{USER}:{PASSWORD}@{URI}:{PORT}/{DB}"
#         engine = create_engine(connection_string)
#         # engine = create_engine(WHOLE_URI)

#     print("🔗 Initial Connection String:", connection_string)
#     print("🔗 Sent Connection string:", engine.url)

#     try:
#         with engine.connect() as connection:
#             # Execute a trivial query to test the connection
#             connection.execute(text("SELECT 1"))

#             print("✅ Connection to the database established successfully.")

#     except SQLAlchemyError as error:
#         print(f"Failed to establish connection to the database: {error}")
#         raise

#     return engine


# def execute_sql(sql: str, engine: sqla.engine.base.Connection) -> None:
#     """
#     Execute a SQL command and provide feedback from the server.

#     Depending on the type of query, prints:
#       - For SELECT queries: the rows returned.
#       - For other queries: the number of affected rows.

#     Parameters:
#         sql (str): The SQL command to execute.

#     Returns:
#         None
#     """

#     try:
#         # engine.begin() because it is a context manager that will automatically commit or rollback the transaction
#         with engine.begin() as connection:
#             print(f"Executing the following SQL command: {sql}")
#             result = connection.exec_driver_sql(sql)
#             print("Query executed successfully.")

#             # Check if the query returned rows (e.g., SELECT statement)
#             if result.returns_rows:
#                 rows = result.fetchall()
#                 print("Query returned the following rows:")
#                 for row in rows:
#                     print(row)

#             else:
#                 rowcount = result.rowcount
#                 print(f"Query executed successfully. Rows affected: {rowcount}")

#     except SQLAlchemyError as error:
#         print(f"Failed to execute query: {error}")
