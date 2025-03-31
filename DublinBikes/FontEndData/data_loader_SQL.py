from sqlalchemy import text
from DublinBikes.SQL_code.sql_utils import get_sql_engine

"""
Not used, but kept for future reference.
"""


def get_station_data(station_id: int) -> dict:
    """
    Retrieve a station's complete data by joining the station and availability tables.
    Picks the availability record with the latest last_update and returns a flat dictionary.
    """

    query = """
        SELECT station_id, address, banking, bonus, bike_stands, name,
               position_lat, position_lng,
               last_update, available_bikes, available_bike_stands, status
        FROM FetchedBikesData 
        WHERE station_id = :station_id
        Order By last_update DESC
        LIMIT 1;
    """

    conn = get_sql_engine()
    try:
        cursor = conn.cursor()
        cursor.execute(query, {"station_id": station_id})

        # Fetch all station records
        rows = cursor.fetchall()
        stations = [dict(row) for row in rows]
        print(stations)
        return stations
    finally:
        conn.close()


def get_all_stations_data_SQL() -> list:
    """
    Retrieve all stations data
    """
    conn = get_sql_engine()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM station")
        # Fetch all station records
        rows = cursor.fetchall()
        stations = []

        for row in rows:
            station = {
                "station_id": row[0],
                "address": row[1],
                "banking": row[2],
                "bonus": row[3],
                "bike_stands": row[4],
                "name": row[5],
                "position": {"lat": row[6], "lng": row[7]},
            }
            stations.append(station)
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
        cursor.execute(
            "SELECT * FROM station WHERE station_id = :station_id",
            {"station_id": station_id},
        )
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
        cursor.execute(query, {"station_id": station_id})
        rows = cursor.fetchall()
        print(rows)
        return [dict(row) for row in rows]
    finally:
        conn.close()
