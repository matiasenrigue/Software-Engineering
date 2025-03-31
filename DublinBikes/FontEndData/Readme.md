# FontendData

The **FontendData** folder is responsible for serving data to the frontend of the Dublin Bikes project. It contains modules that load bike station and weather data from various sources (SQL database and CSV files), provide real-time updates by fetching data from external APIs, and manage caching to improve performance.

## Module Overview

- **data_loader_SQL.py**  
  Contains functions to retrieve bike station data (including detailed station information and daily availability records) from the SQL database. Although these functions are not currently in active use, they are kept for future reference.

- **data_loader_csv.py**  
  Provides functions to read bike station and weather data from CSV files. Although these functions are not currently in active use, they are kept for future reference.

- **data_realtime_bikes.py**  
  Implements functions to fetch real-time bike station data from the JCDecaux API. It includes caching logic to check for recent data (within 5 minutes) before making a new API call, and it saves the retrieved data into the cache database.

- **data_realtime_weather.py**  
  Contains functions to fetch current and forecast weather data from the OpenWeather API. The module first checks the cache (using a 15-minute window for current data) and cleans outdated records before inserting new data. It also handles both current and forecast weather requests.

- **manage_cache.py**  
  Provides functionality to clean the cache by deleting outdated records from the weather and bike data tables. It updates a cache file to ensure that the cleaning process occurs only once per day.

## Usage

Each module is designed to be imported by other parts of the application (e.g., Flask routes) to serve data to the frontend. For example:
- The Flask application might call `get_current_bikes_data()` to get up-to-date bike availability information.
- Weather data for the dashboard is fetched via `get_current_weather_data()` or `get_forecast_weather_data()`.

## Notes

- The modules include detailed docstrings that describe their functionality, input parameters, and return types in accordance with PEP guidelines.
- Although some functions are not used in the current implementation, they have been retained for potential future enhancements or reference.
- The caching mechanism (implemented in `manage_cache.py`) ensures that outdated data is removed daily to maintain the relevance and performance of the application.

---

For any further modifications or questions regarding this module, please refer to the inline documentation.
