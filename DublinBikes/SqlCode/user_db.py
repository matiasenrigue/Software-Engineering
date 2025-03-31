from DublinBikes.SqlCode.sql_utils import get_sql_engine, execute_sql

import sqlite3
from typing import Optional, Union, Dict


def register_user(
    email: str,
    username: str,
    first_name: str,
    last_name: str,
    password: str,
    default_station: int,
) -> bool:
    """
    Inserts a new user into the user table of the SQLite database.

    The function expects the table 'user' to have the following structure:
        email TEXT PRIMARY KEY,
        username TEXT UNIQUE,
        first_name TEXT,
        last_name TEXT,
        password TEXT,
        default_station INTEGER

    Parameters:
        email (str): User's email address (primary key).
        username (str): Unique username.
        first_name (str): User's first name.
        last_name (str): User's last name.
        password (str): User's password (not encrypted).
        default_station (int): The default bike station ID associated with the user.

    Returns:
        bool: True if the user was registered successfully, False if an integrity error occurred (e.g. duplicate email or username).
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
    Retrieves a user's data from the SQLite database based on their email.

    Parameters:
        email (str): The email of the user to retrieve.

    Returns:
        Optional[Dict[str, Union[str, int]]]: A dictionary with the user's data if found, or None if no user with the given email exists.
    """
    conn = get_sql_engine()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user WHERE email = ?", (email,))
        row = cursor.fetchone()
        if row is not None:
            # Convert the sqlite3.Row to a standard dictionary.
            return dict(row)
        return None
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
    Updates a user's profile information except for the email.
    Returns True on success, False if an error occurs (e.g., integrity issues).
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
