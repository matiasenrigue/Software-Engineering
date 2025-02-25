from sqlalchemy import create_engine, text
from DublinBikes.Utils.params import *
import sqlalchemy as sqla
from sqlalchemy.exc import SQLAlchemyError



def get_sql_engine() -> sqla.engine.base.Connection:
    """
    Function to get the engine to be used to connect to the database.
    
    :return: the engine to be used to connect to the database
    """
    
    # If local is True, the connection is made to the local database
    # If local is False, the connection is made to the remote database
    local: bool = LOCAL_RUNNING
    
    print("🌐 Connecting to the database")
    
    if local:
        engine = create_engine(f"mysql+mysqlconnector://{LOCAL_USER}:{LOCAL_PASSWORD}@{LOCAL_URI}:{PORT}/{LOCAL_DB}")
    else:
        # engine = create_engine(f"mysql+mysqlconnector://{USER}:{PASSWORD}@{URI}:{PORT}/{DB}")
        engine = create_engine(WHOLE_URI)
    
    try:
        with engine.connect() as connection:
            # Execute a trivial query to test the connection
            connection.execute(text("SELECT 1"))

            print("✅ Connection to the database established successfully.")
        
    except SQLAlchemyError as error:
        print(f"Failed to establish connection to the database: {error}")
        raise  

    return engine




    
    
    
def execute_sql(sql: str, engine: sqla.engine.base.Connection) -> None:
    """
    Execute a SQL command and provide feedback from the server.

    Depending on the type of query, prints:
      - For SELECT queries: the rows returned.
      - For other queries: the number of affected rows.

    Parameters:
        sql (str): The SQL command to execute.

    Returns:
        None
    """
    
    try:
        # engine.begin() because it is a context manager that will automatically commit or rollback the transaction
        with engine.begin() as connection:
            print(f"Executing the following SQL command: {sql}")
            result = connection.exec_driver_sql(sql)
            print("Query executed successfully.")
            
            # Check if the query returned rows (e.g., SELECT statement)
            if result.returns_rows:
                rows = result.fetchall()
                print("Query returned the following rows:")
                for row in rows:
                    print(row)
            
            else:
                rowcount = result.rowcount
                print(f"Query executed successfully. Rows affected: {rowcount}")
                
    except SQLAlchemyError as error:
        print(f"Failed to execute query: {error}")







##########################################################################################
# The following functions are used to create the tables in the database
##########################################################################################



def create_data_base():
    engine = get_sql_engine()

    # Station table
    sql_station_table = '''
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
    '''

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

    # Execute all the CREATE TABLE statements
    execute_sql(sql_station_table, engine)
    execute_sql(sql_availability_table, engine)
    execute_sql(sql_current_table, engine)

    
    
    

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
    execute_sql("select * from availability where available_bike_stands > 20 LIMIT 5", engine)
    execute_sql("select * from current where temp > 20", engine)


if __name__ == "__main__":
    create_data_base()
    test_queries()