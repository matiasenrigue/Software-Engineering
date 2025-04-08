# Tests Module

The **Tests** folder contains a comprehensive suite of unit and integration tests designed to validate the functionality and reliability of the Dublin Bikes project. These tests cover data retrieval, caching logic, API endpoints, user management, and overall web application behavior.

## Overview

The tests are organized by the application’s functional areas. They ensure that:
- Real-time weather and bike data are correctly fetched and cached.
- The cache cleaning mechanism properly removes outdated data.
- User registration, authentication, and profile updates work as expected.
- All Flask routes and API endpoints respond correctly and handle errors gracefully.

## Directory Structure

```
Tests/
├── test_current_weather.py    # Validates current weather data retrieval and caching.
├── test_forecast_weather.py   # Checks forecast weather API functionality and cache consistency.
├── test_manage_cache.py       # Ensures the cache cleaning process works as intended.
├── test_realtime_bikes.py     # Tests real-time bike data retrieval and caching behavior.
├── test_user_logic.py         # Verifies user registration, lookup, and profile update functionality.
└── test_web.py                # Performs integration tests on Flask routes and API endpoints.
```

## Running the Tests

All tests can be executed using Python’s built-in unittest framework. From the project root, run:

```bash
python -m unittest discover -s DublinBikes/Tests -p "test_*.py"
```

This command will automatically discover and run all test files starting with `test_` in the `DublinBikes/Tests` directory.

## Test Descriptions

- **test_current_weather.py:**  
  Tests the retrieval and caching of current weather data from the OpenWeather API, ensuring that repeated calls within the cache interval return consistent results.

- **test_forecast_weather.py:**  
  Validates that the forecast weather API correctly returns a JSON dictionary with key forecast data (e.g., temperature) and that caching works for forecast requests.

- **test_manage_cache.py:**  
  Confirms that the cache cleaning function properly deletes outdated records from both weather and bikes tables and updates the cache file accordingly.

- **test_realtime_bikes.py:**  
  Checks that real-time bike data is fetched and stored in the cache correctly, and that consecutive calls return identical results.

- **test_user_logic.py:**  
  Tests user management functions such as user registration, duplicate prevention, profile updates, and user lookup by email.

- **test_web.py:**  
  Provides integration tests for the Flask web application routes (home page, station details, API endpoints, login/logout, registration, and profile editing) to ensure end-to-end functionality.

---

By running these tests regularly, you can ensure the robustness and correctness of the Dublin Bikes project.
