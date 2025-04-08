import sqlite3
from typing import Optional, Union, Dict
from DublinBikes.SqlCode.sql_utils import get_sql_engine

"""
Module: user_db
===============

This module provides functions for managing user information in the SQLite database.
It includes functionality to register new users, retrieve user data by email, and update existing user profiles.

Functions:
    - register_user: Inserts a new user into the "user" table.
    - get_user_by_email: Retrieves user details based on the provided email address.
    - update_user_profile: Updates the profile information of an existing user (excluding the email).
"""



def register_user(
    email: str,
    username: str,
    first_name: str,
    last_name: str,
    password: str,
    default_station: int,
) -> bool:
    """
    Register a new user in the database.

    Inserts a new record into the "user" table using the provided user details.
    The email serves as the primary key and the username must be unique.

    Parameters:
        email (str): The user's email address.
        username (str): The user's unique username.
        first_name (str): The user's first name.
        last_name (str): The user's last name.
        password (str): The user's password (stored in plain text).
        default_station (int): The default bike station ID associated with the user.

    Returns:
        bool: True if the registration is successful; False if an integrity error occurs.
    """
    conn = get_sql_engine()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO user (email, username, first_name, last_name, password, default_station)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (email, username, first_name, last_name, password, default_station),
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError as e:
        print("Error registering user:", e)
        return False
    finally:
        conn.close()


def get_user_by_email(email: str) -> Optional[Dict[str, Union[str, int]]]:
    """
    Retrieve user information based on the email address.

    Queries the "user" table for a record matching the provided email.

    Parameters:
        email (str): The email address of the user to retrieve.

    Returns:
        Optional[Dict[str, Union[str, int]]]: A dictionary with user details if found; otherwise, None.
    """
    conn = get_sql_engine()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user WHERE email = ?", (email,))
        row = cursor.fetchone()
        return dict(row) if row is not None else None
    finally:
        conn.close()


def update_user_profile(
    email: str,
    username: str,
    first_name: str,
    last_name: str,
    password: str,
    default_station: int,
) -> bool:
    """
    Update an existing user's profile information.

    Updates the username, first name, last name, password, and default station for the user identified by email.
    The email itself remains unchanged.

    Parameters:
        email (str): The user's email address (identifier).
        username (str): The new username.
        first_name (str): The new first name.
        last_name (str): The new last name.
        password (str): The new password.
        default_station (int): The new default bike station ID.

    Returns:
        bool: True if the update was successful; False if an integrity error occurs.
    """
    conn = get_sql_engine()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE user
            SET username = ?, first_name = ?, last_name = ?, password = ?, default_station = ?
            WHERE email = ?
            """,
            (username, first_name, last_name, password, default_station, email),
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError as e:
        print("Error updating user profile:", e)
        return False
    finally:
        conn.close()
