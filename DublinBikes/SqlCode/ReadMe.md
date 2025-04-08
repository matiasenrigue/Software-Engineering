# SqlCode Module

## Overview

The **SqlCode** module provides core functionalities for managing the SQLite database used in the Dublin Bikes project.
It includes utilities for establishing database connections, executing SQL commands, and setting up the database schema.
In addition, the module offers functions for user management, including registration, data retrieval, and profile updates.

## Folder Structure

```
SqlCode/
├── __init__.py
├── sql_utils.py      # Contains utility functions for database connection, SQL command execution, and schema creation.
└── user_db.py        # Provides functions to register users, retrieve user data by email, and update user profiles.
```

## Files Description

- **sql_utils.py**:  
  This file includes:
  - `get_db_path()`: Determines and returns the absolute path to the SQLite database file.
  - `get_sql_engine()`: Creates and returns a connection to the SQLite database, configured for named row access.
  - `execute_sql()`: Executes SQL commands and prints the results or the number of rows affected.
  - `create_data_base()`: Creates the necessary tables (user, station, availability, current, FetchedWeatherData, FetchedBikesData) if they do not already exist.
  - `test_queries()`: Runs sample queries to test the database setup.

- **user_db.py**:  
  This file provides functions for interacting with user data stored in the SQLite database:
  - `register_user()`: Inserts a new user record into the "user" table.
  - `get_user_by_email()`: Retrieves a user's information based on their email address.
  - `update_user_profile()`: Updates an existing user's profile information (except the email).

## Usage

1. **Database Setup:**  
   To set up the database and create all necessary tables, run the following command from the SqlCode folder:
   ```bash
   python sql_utils.py
   ```
   This script will also execute test queries to verify the setup.

2. **User Management:**  
   Functions in `user_db.py` are designed to be called by other parts of the Dublin Bikes project (e.g., web application routes) for registering users, retrieving user data, and updating profiles.

## Notes

- The module is designed for local SQLite usage. Legacy AWS RDS code using SQLAlchemy is present only as commented-out code.
- Make sure that the "data" folder exists at the project root; it is used to store the SQLite database file.