# Dublin Bikes – Developer Manual

**Version:** 0.0.0  
**Last Updated:** April 9th 2025

---

## Table of Contents

- [Introduction](#introduction)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Setting Up the Development Environment](#setting-up-the-development-environment)
- [Architecture and Code Structure](#architecture-and-code-structure)
  - [Module Overview](#module-overview)
    - [DataFrontend](#datafrontend)
    - [DataMining](#datamining)
    - [FlaskApp](#flaskapp)
    - [MachineLearning](#machinelearning)
    - [SqlCode](#sqlcode)
    - [Tests](#tests)
    - [Utils](#utils)
- [API Documentation](#api-documentation)
- [Configuration and Coding Standards](#configuration-and-coding-standards)
- [Extending the Software](#extending-the-software)
- [Deployment and Maintenance](#deployment-and-maintenance)
- [Testing and Debugging](#testing-and-debugging)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [Additional Resources](#additional-resources)

---

## Introduction

The Dublin Bikes Developer Manual is designed specifically for developers, maintainers, and technical contributors. It details the internal architecture, design decisions, and implementation guidelines for the Dublin Bikes project—a comprehensive system that gathers real-time bike station data and weather information, supports historical data analysis, and utilizes machine learning models for ride prediction.

This document covers:
- An overview of the system’s modules.
- Setup instructions for a development environment.
- Detailed walkthroughs of key modules.
- Guidelines for integration, extension, deployment, and testing.

---

## Getting Started

### Prerequisites

Before you begin, make sure you have the following installed:
- **Python 3.11.0** or the version specified in the project.
- **pip** package manager.
- **Virtual environment manager:** Preferably [pyenv](https://github.com/pyenv/pyenv) with [pyenv-virtualenv](https://github.com/pyenv/pyenv-virtualenv) or your favorite virtual environment tool.
- **SQLite:** For local database management.

### Setting Up the Development Environment

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/<your-org>/DublinBikes.git
   cd DublinBikes
   ```

2. **Set Up the Virtual Environment:**

   Using the provided Makefile, you can run:

   ```bash
   make setup
   make activate
   ```

   *Note: The `activate` target in the Makefile prints the command you need to run to activate the virtual environment.*

3. **Install Dependencies:**

   Install the required packages:

   ```bash
   pip install -r requirements.txt
   # Alternatively, install in editable mode:
   pip install -e .
   ```

4. **Database Setup:**

   Create the necessary SQLite tables by running:

   ```bash
   make create-db
   ```

   This command executes the scripts in `SqlCode/sql_utils.py` to create tables for users, stations, availability, weather, and bikes data.

---

## Architecture and Code Structure

The project is organized into several main directories. Below is an overview of each module:

### Module Overview

#### DataFrontend

- **Purpose:**  
  Provides modules to load bike and weather data (from SQL or CSV) and fetch real-time updates via external APIs.
- **Key Files:**
  - `data_loader_SQL.py` – Retrieves station data from the SQL database.
  - `data_loader_csv.py` – Reads bike and weather data from CSV files (legacy functionality).
  - `data_realtime_bikes.py` – Handles API calls for real-time bike station data with caching.
  - `data_realtime_weather.py` – Fetches and caches current and forecast weather data from the OpenWeather API.
  - `manage_cache.py` – Cleans outdated cache records (invoked daily).

#### DataMining

- **Purpose:**  
  Scrapes historical data from external APIs (JCDecaux and OpenWeather) to build a database for analytics and machine learning.
- **Key Files:**
  - `general_scrapper.py` – Orchestrates data collection using threading.
  - `local_scrapping.py` – Contains utility functions for local storage (CSV files).
  - `scrapper_jc_decaux.py` – Scrapes bike station data and populates the database.
  - `scrapper_open_weather.py` – Fetches weather data and stores it accordingly.

#### FlaskApp

- **Purpose:**  
  Contains the Flask web application serving as the front-end interface and API gateway.
- **Structure:**
  - `__init__.py` – Initializes and configures the Flask app.
  - `routes.py` – Defines endpoints for web pages (home, login, registration, profiles) and API endpoints.
  - **Static Files:**  
    Includes JavaScript files (for maps, bikes, predictions, weather), CSS, and image assets.
  - **Templates:**  
    Jinja2 templates (e.g., `home.html`, `login.html`, `station.html`) used for rendering dynamic content.

#### MachineLearning

- **Purpose:**  
  Hosts pre-trained machine learning models for ride predictions and contains notebooks for model training and optimization.
- **Key Files:**
  - `predict_availability.py` – Loads models and performs prediction logic.
  - Jupyter notebooks –  
    - `training_part1_model_selection.ipynb`
    - `training_part2_model_size_reduction.ipynb`
  - **Models Directory:**  
    Contains station-specific pickle files (e.g., `model_station_1.pkl`, `model_station_2.pkl`, …).

#### SqlCode

- **Purpose:**  
  Provides database management functionalities.
- **Key Files:**
  - `sql_utils.py` – Functions to manage database connections and execute SQL commands.
  - `user_db.py` – APIs for registering, retrieving, and updating user data.

#### Tests

- **Purpose:**  
  Implements unit and integration tests to ensure robust functionality.
- **Files:**  
  Contains various test files for each module (e.g., `test_current_weather.py`, `test_user_logic.py`, `test_web.py`).

#### Utils

- **Purpose:**  
  Contains configuration files and utility settings.
- **Key File:**
  - `params.py` – Holds API keys, URIs, and environment-specific settings.

---

## API Documentation

The Flask app exposes several API endpoints. Key endpoints include:

- **GET `/api/current_weather`**  
  *Description:* Returns the current weather data in JSON format.  
  *Response Example:*  
  ```json
  {
      "temp": 15.2,
      "humidity": 72,
      "timestamp_weatherinfo": "2025-04-02T14:30:00"
  }
  ```
  
- **GET `/api/forecast_weather?forecast_type=hourly&target_datetime=2025-04-02T14:30:00`**  
  *Description:* Returns forecast weather data matching the target datetime. Returns a 400 error if required parameters are missing.

- **GET `/api/current_bikes`**  
  *Description:* Provides current bike availability from the cache or fetches new data if no cache is available.

- **POST `/api/ride_prediction`**  
  *Description:* Accepts a JSON payload with prediction data (timestamp, temperature, humidity, origin and destination station IDs) and returns predicted values.  
  *Payload Example:*  
  ```json
  {
      "timestamp": "2025-04-02T14:30:00",
      "temperature": 15.2,
      "humidity": 72,
      "origin_station_id": 1,
      "destination_station_id": 10
  }
  ```
  *Response Example:*  
  ```json
  {
      "prediction": {
          "origin_station_id": 5,
          "destination_station_id": 3
      }
  }
  ```

- **User Authentication Endpoints:**  
  Routes such as `/login`, `/logout`, `/register`, and `/edit_profile` provide HTML-based interfaces for user management.

For further API details, refer to inline documentation within each route in `FlaskApp/routes.py`.

---

## Configuration and Coding Standards

- **Configuration Files:**  
  - `Utils/params.py` holds all the environment-specific keys and URIs. Adjust this file as needed before deployment.
  - Environment files such as `.envrc` and `.python-version` are used to maintain consistency.

- **Coding Standards:**  
  - Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) guidelines for Python code.
  - Ensure all functions have clear docstrings that describe inputs, outputs, and side effects.
  - Use consistent naming conventions for variables and functions.
  - Commit messages should be clear and descriptive about the changes being introduced.

---

## Extending the Software

Developers looking to extend the Dublin Bikes project may consider the following areas:

- **New Data Sources:**  
  To incorporate additional APIs or data sources (e.g., extra weather parameters), add new modules under `DataMining` and integrate them with caching modules in `DataFrontend`.

- **Enhanced Machine Learning Models:**  
  Update or retrain prediction models in the `MachineLearning` module using new data. Modify `predict_availability.py` to handle additional features if required.

- **New API Endpoints:**  
  Extend `FlaskApp/routes.py` with new endpoints or modify existing ones for additional functionality. Always include comprehensive tests for new routes.

- **Plugin Architecture:**  
  Identify extension points where new functionalities can be plugged in (e.g., new user management features, extra chart types in station details).

---

## Deployment and Maintenance

- **Deployment:**  
  - Use the `run.py` script to launch the Flask application.
  - The Makefile provides several targets (e.g., `runserver-local`, `runserver-ec2`) for different environments.
  - Prior to deployment, ensure that all environment variables and API keys in `Utils/params.py` are updated accordingly.

- **Maintenance:**  
  - Regularly run test suites using `make runtest` to ensure that new changes do not break existing functionalities.
  - Monitor log outputs and error messages (printed via console) for quick debugging.
  - Review and clean the cache by verifying the operation of `manage_cache.py`.

---

## Testing and Debugging

- **Testing:**  
  All unit and integration tests are located under the `Tests/` directory. Run them using:
  ```bash
  python -m unittest discover -s DublinBikes/Tests -p "test_*.py"
  ```
  Alternatively, use the Makefile target:
  ```bash
  make runtest
  ```

- **Debugging:**  
  - Use debugging print statements and log messages embedded in the code.
  - The Makefile target `debug-env` can help verify your current development environment settings.
  - For web-related errors, check the browser’s developer console and Flask’s debug output.

---

## Troubleshooting

- **Database Connection Issues:**  
  Ensure that the SQLite database file exists under the `data/` folder and that the file permissions allow read/write access. Use `sql_utils.py` to test the connection manually.

- **API Key Errors:**  
  Verify that the API keys in `Utils/params.py` are current and correctly configured.

- **Cache Not Updating:**  
  If caching does not behave as expected, check the logic in `manage_cache.py` and inspect the contents of `lastcachedelete.txt`.

- **Module Import Errors:**  
  Confirm that the virtual environment is activated and that your `PYTHONPATH` includes the repository root.

---

## Contributing

Developers are encouraged to contribute improvements or fixes:
1. Fork the repository.
2. Create a feature branch based on the latest `main` branch.
3. Add your changes with clear commit messages and comprehensive tests.
4. Submit a Pull Request describing your changes and the impact on the system.

For major changes, please open a discussion issue before starting development.

---

## Additional Resources

- [PEP 8 – Style Guide for Python Code](https://www.python.org/dev/peps/pep-0008/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [SQLite Documentation](https://www.sqlite.org/docs.html)
- [Google Maps API Documentation](https://developers.google.com/maps/documentation)
- [JCDecaux API Documentation](https://developer.jcdecaux.com/)
- [OpenWeatherMap API Documentation](https://openweathermap.org/api)

---
