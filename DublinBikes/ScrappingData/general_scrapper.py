import argparse
import threading

from DublinBikes.ScrappingData.scrapper_jc_decaux import main_data_scrapper_bikes
from DublinBikes.ScrappingData.scrapper_open_weather import main_data_scrapper_weather
from DublinBikes.ScrappingData.local_scrapping import create_data_file
from DublinBikes.Utils.sql_utils import get_sql_engine


def main_data_scrapper() -> None:

    # Parse the CLI argument to set save_to_db (default False)
    # Set the variable to save the data to the database
    # False to save to a file, True to save to the database
    parser = argparse.ArgumentParser(description="Scrape data from APIs")
    parser.add_argument(
        "--save-to-db",
        action="store_true",
        default=False,
        help="If set, save scraped data to the database (default: False, saves to CSV)"
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
        

    # Run the two scrappers in parallel using threads
    t_bikes = threading.Thread(target=main_data_scrapper_bikes, args=bikes_args)
    t_weather = threading.Thread(target=main_data_scrapper_weather, args=weather_args)

    t_bikes.start()
    t_weather.start()

    t_bikes.join()
    t_weather.join()



if __name__ == "__main__":
    main_data_scrapper()
