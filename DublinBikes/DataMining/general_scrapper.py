import argparse
import threading

from DublinBikes.DataMining.scrapper_jc_decaux import main_data_scrapper_bikes
from DublinBikes.DataMining.scrapper_open_weather import main_data_scrapper_weather
from DublinBikes.DataMining.local_scrapping import create_data_file
from DublinBikes.SqlCode.sql_utils import get_sql_engine

"""
Module: general_scrapper
------------------------
This module orchestrates the scraping of historical bike and weather data from their respective APIs.
The scraped data is intended to populate a historical database for:
    - Training machine learning models to predict bike availability based on day, hour, and weather.
    - Displaying availability statistics on web pages.
The module supports saving the scraped data either to CSV files or directly to a SQL database.
The scraping processes for bikes and weather run concurrently using threading.
"""


def main_data_scrapper() -> None:
    """
    Main function to initiate data scraping.

    This function parses command-line arguments to determine whether to save scraped data to the SQL database
    (using '--save-to-db') or to CSV files (default behavior). It then starts the bike and weather scrapers
    concurrently using threads, and waits for both threads to complete.

    Returns:
        None
    """
    parser = argparse.ArgumentParser(
        description="Scrape historical data from APIs for building a historical database"
    )
    parser.add_argument(
        "--save-to-db",
        action="store_true",
        default=False,
        help="If set, save scraped data to the SQL database (default: False, saves to CSV)",
    )
    args = parser.parse_args()
    save_to_db: bool = args.save_to_db

    if save_to_db:
        engine = get_sql_engine()
        bikes_args = (save_to_db, engine, None)
        weather_args = (save_to_db, engine, None)
    else:
        bikes_data_file = create_data_file("bikes")
        weather_data_file = create_data_file("weather")
        bikes_args = (save_to_db, None, bikes_data_file)
        weather_args = (save_to_db, None, weather_data_file)

    t_bikes = threading.Thread(target=main_data_scrapper_bikes, args=bikes_args)
    t_weather = threading.Thread(target=main_data_scrapper_weather, args=weather_args)

    t_bikes.start()
    t_weather.start()

    t_bikes.join()
    t_weather.join()


if __name__ == "__main__":
    main_data_scrapper()
