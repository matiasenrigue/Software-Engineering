from sqlalchemy import text
from DublinBikes.Utils.sql_utils import get_sql_engine




def get_station_data(station_id: int) -> dict:
    """
    Retrieve a station's complete data by joining the station and availability tables.
    Picks the availability record with the latest last_update and returns a flat dictionary.
    """
    engine = get_sql_engine()
    query = text("""
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
    """)
    
    with engine.connect() as conn:
        row = conn.execute(query, {'station_id': station_id}).mappings().first()
    
    if row is None:
        return {}
    
    return dict(row)

