from sqlalchemy import text
from DublinBikes.SQL_code.sql_utils import get_sql_engine




def get_station_data(station_id: int) -> dict:
    """
    Retrieve a station's complete data by joining the station and availability tables.
    Picks the availability record with the latest last_update and returns a flat dictionary.
    """
    query = """
        SELECT s.station_id, s.address, s.banking, s.bonus, s.bike_stands, s.name,
               s.position_lat, s.position_lng,
               a.last_update, a.available_bikes, a.available_bike_stands, a.status
        FROM station s
        JOIN (
            SELECT station_id, MAX(last_update) AS last_update
            FROM availability
            GROUP BY station_id
        ) AS latest ON s.station_id = latest.station_id
        JOIN availability a ON a.station_id = latest.station_id AND a.last_update = latest.last_update
        WHERE s.station_id = :station_id;
    """
    
    conn = get_sql_engine()
    try:
        cursor = conn.cursor()
        cursor.execute(query, {'station_id': station_id})

        # Fetch all station records
        rows = cursor.fetchall()
        stations = [dict(row) for row in rows]
        print(stations)
        return stations
    finally:
        conn.close()
    


def get_all_stations_data() -> list:
    """
    Retrieve all stations data
    """    
    conn = get_sql_engine()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM station")
        # Fetch all station records
        rows = cursor.fetchall()
        stations = [dict(row) for row in rows]
        print(stations)
        return stations
    finally:
        conn.close()
        



def get_one_station_data(station_id: int) -> dict:
    """
    Retrieve one station data
    """    
    conn = get_sql_engine()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM station WHERE station_id = :station_id", {'station_id': station_id})
        row = cursor.fetchone()
        return dict(row) if row is not None else {}
    finally:
        conn.close()
        
        




def get_station_availability_daily(station_id: int) -> list:
    """
    Retrieve all availability records for the given station for the current day.
    Assumes that 'last_update' is stored as a DATETIME string.
    """
    
    # The scrapped data is from March 3, so we only show data from that day
    query = """
        SELECT last_update, available_bikes, available_bike_stands
        FROM availability
        WHERE station_id = :station_id
            AND DATE(last_update) = '2025-03-03'
        ORDER BY last_update ASC;
    """
    conn = get_sql_engine()
    try:
        cursor = conn.cursor()
        cursor.execute(query, {'station_id': station_id})
        rows = cursor.fetchall()
        print(rows)
        return [dict(row) for row in rows]
    finally:
        conn.close()
