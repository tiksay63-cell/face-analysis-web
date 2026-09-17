import sqlite3
from datetime import date
from pathlib import Path


DB_PATH = Path("data/users.db")


def init_database():
    DB_PATH.parent.mkdir(exist_ok=True)

    connection = sqlite3.connect(DB_PATH)

    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            analysis_date TEXT,
            free_analyses INTEGER DEFAULT 0,
            paid_analyses INTEGER DEFAULT 0
        )
    """)

    connection.commit()
    connection.close()


def get_user(user_id):
    connection = sqlite3.connect(DB_PATH)

    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM users WHERE user_id = ?",
        (user_id,)
    )

    user = cursor.fetchone()

    connection.close()

    return user


def reset_if_new_day(user_id):

    today = str(date.today())

    connection = sqlite3.connect(DB_PATH)

    cursor = connection.cursor()

    cursor.execute(
        "SELECT analysis_date FROM users WHERE user_id = ?",
        (user_id,)
    )

    result = cursor.fetchone()

    if result is None:

        cursor.execute("""
            INSERT INTO users
            (user_id, analysis_date, free_analyses, paid_analyses)
            VALUES (?, ?, 0, 0)
        """, (user_id, today))

    elif result[0] != today:

        cursor.execute("""
            UPDATE users
            SET analysis_date = ?,
                free_analyses = 0
            WHERE user_id = ?
        """, (today, user_id))

    connection.commit()
    connection.close()


def get_free_analyses(user_id):

    reset_if_new_day(user_id)

    connection = sqlite3.connect(DB_PATH)

    cursor = connection.cursor()

    cursor.execute(
        "SELECT free_analyses FROM users WHERE user_id = ?",
        (user_id,)
    )

    result = cursor.fetchone()

    connection.close()

    return result[0] if result else 0


def add_free_analysis(user_id):

    reset_if_new_day(user_id)

    connection = sqlite3.connect(DB_PATH)

    cursor = connection.cursor()

    cursor.execute("""
        UPDATE users
        SET free_analyses = free_analyses + 1
        WHERE user_id = ?
    """, (user_id,))

    connection.commit()
    connection.close()
