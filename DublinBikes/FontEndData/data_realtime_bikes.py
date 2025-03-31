import datetime
import json
from DublinBikes.SQL_code.sql_utils import get_sql_engine
from DublinBikes.ScrappingData.scrapper_jc_decaux import get_data_from_jcdecaux


def save_bikes_data_to_cache_db(bikes_data: list, return_rows: bool = True) -> list:
    """
    Save bikes data (from the bikes API) into the cache database.
    All inserted records share the same time_requested.
    Now includes extra info: address, banking, bonus, bike_stands, name,
    position_lat, position_lng.
    """
    conn = get_sql_engine()
    inserted_records = []
    try:
        # Use a single timestamp for this snapshot
        time_requested = datetime.datetime.now()
        cursor = conn.cursor()

        for station in bikes_data:
            # Get fields from API response.
            station_id = station.get("number")
            available_bikes = station.get("available_bikes")
            available_bike_stands = station.get("available_bike_stands")
            status = station.get("status")
            last_update_ms = station.get("last_update")
            last_update = (
                datetime.datetime.fromtimestamp(last_update_ms / 1000)
                if last_update_ms
                else None
            )

            # Extra fields from API (make sure your API returns these)
            address = station.get("address")
            banking = station.get("banking")
            bonus = station.get("bonus")
            bike_stands = station.get("bike_stands")
            name = station.get("name")
            # For position, assume the API returns a dictionary with keys 'lat' and 'lng'
            position = station.get("position", {})
            position_lat = position.get("lat")
            position_lng = position.get("lng")

            insert_query = """
            INSERT INTO FetchedBikesData (
                time_requested, station_id, available_bikes, available_bike_stands, status, last_update,
                address, banking, bonus, bike_stands, name, position_lat, position_lng
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """
            cursor.execute(
                insert_query,
                (
                    time_requested,
                    station_id,
                    available_bikes,
                    available_bike_stands,
                    status,
                    last_update,
                    address,
                    banking,
                    bonus,
                    bike_stands,
                    name,
                    position_lat,
                    position_lng,
                ),
            )
            if return_rows:
                inserted_records.append(
                    {
                        "time_requested": time_requested,
                        "station_id": station_id,
                        "available_bikes": available_bikes,
                        "available_bike_stands": available_bike_stands,
                        "status": status,
                        "last_update": last_update,
                        "address": address,
                        "banking": banking,
                        "bonus": bonus,
                        "bike_stands": bike_stands,
                        "name": name,
                        "position": {"lat": position_lat, "lng": position_lng},
                    }
                )
        conn.commit()
        return inserted_records
    finally:
        conn.close()


def get_current_bikes_data():
    """
    Retrieve bikes data from cache if it was fetched within the last 5 minutes.
    Otherwise, fetch new data from the bikes API, cache it, and return it.
    """
    conn = get_sql_engine()
    try:
        five_minutes_ago = datetime.datetime.now() - datetime.timedelta(minutes=5)
        cursor = conn.cursor()
        query = """
        SELECT * FROM FetchedBikesData
        WHERE time_requested >= ?
        ORDER BY time_requested DESC;
        """
        cursor.execute(query, (five_minutes_ago,))
        rows = cursor.fetchall()
    finally:
        conn.close()

    if rows:
        print("Using cached data")
        bikes_data = []
        for row in rows:
            # Convert each row to a dictionary
            bikes_data.append(
                {
                    "time_requested": row[0],
                    "station_id": row[1],
                    "available_bikes": row[2],
                    "available_bike_stands": row[3],
                    "status": row[4],
                    "last_update": row[5],
                    "address": row[6],
                    "banking": row[7],
                    "bonus": row[8],
                    "bike_stands": row[9],
                    "name": row[10],
                    "position": {"lat": row[11], "lng": row[12]},
                }
            )
        print(bikes_data)
        return bikes_data

    else:
        bikes_text = get_data_from_jcdecaux()
        if bikes_text:
            bikes_data = json.loads(bikes_text)
            inserted_records = save_bikes_data_to_cache_db(bikes_data, return_rows=True)
            print(inserted_records)
            return inserted_records
        else:
            return {"error": "Unable to fetch bikes data"}
