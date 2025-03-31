# DataMining Module


## Overview

The **DataMining** module is designed to fetch and store historical data from external APIs—specifically, the JCDecaux bike station API and the OpenWeatherMap API. The primary goal is to build a historical database that serves two main purposes:

- **Machine Learning:**  
  Train prediction models to forecast bike availability at each station based on the day, hour, and weather conditions.

- **Data Display & Analysis:**  
  Provide availability statistics and historical insights on various frontend pages.

The module supports two data-saving modes:
- **SQL Database:** For robust, queryable storage (the preferred option).
- **CSV Files:** As a backup or for offline analysis (legacy functionality).

## Directory Structure

```
DataMining/
├── __init__.py
├── export_to_csv.py       # Exports historical bike and weather data from the SQL DB to CSV files.
├── general_scrapper.py    # Orchestrates the scraping process using threading for concurrent bike and weather data collection.
├── local_scrapping.py     # Contains utility functions to manage local file storage for scraped data.
├── scrapper_jc_decaux.py  # Fetches bike station data from the JCDecaux API and saves it to the database.
└── scrapper_open_weather.py  # Fetches current weather data from the OpenWeatherMap API and saves it to the database.
```

## Features

- **Data Collection:**  
  Retrieves historical data for bike availability and weather information from external APIs.

- **Flexible Storage:**  
  Supports saving data directly to a SQL database (preferred) or as CSV files (for legacy/backups).

- **Concurrency:**  
  Uses threading in the `general_scrapper.py` to run bike and weather scrapers concurrently.

- **Historical Database:**  
  The collected data is intended for building a robust historical database, which is essential for training machine learning models to predict bike availability and for displaying historical trends on web pages.


## Usage

### Command-Line Interface

To start the data scraping process, run the `general_scrapper.py` script. By default, data is saved to CSV files. To save data directly to the SQL database, use the `--save-to-db` flag:

```bash
python general_scrapper.py --save-to-db
```

### Modules in Detail

- **export_to_csv.py:**  
  Contains functions to export bike and weather data from the SQL database into CSV files for offline analysis or backup.

- **general_scrapper.py:**  
  Serves as the main entry point. It parses command-line arguments, sets up the required resources (SQL engine or file paths), and starts the bike and weather scrapers concurrently using threads.

- **local_scrapping.py:**  
  Provides helper functions to ensure that a local data folder exists, create timestamped files, and save data (converting JSON to CSV when needed).

- **scrapper_jc_decaux.py:**  
  Contains functions to fetch bike station data from the JCDecaux API. It parses the data and saves station and availability information into the SQL database (or into a CSV file, based on the configuration).

- **scrapper_open_weather.py:**  
  Fetches current weather data for Dublin from the OpenWeatherMap API, processes it, and saves the data into the SQL database (or CSV file).
