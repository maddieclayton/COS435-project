# Creates and manages the ratings DB.
import sqlite3
import os

db_file = 'data.db'


def create_db():
    """
    Creates the DB file and the tables. Fails with an error if the DB already exists.
    """
    if os.path.isfile(db_file):
        print("DB already exists!")
        return

    # Create it!
    conn = sqlite3.connect(db_file)
    conn.execute('CREATE TABLE tweets (id INTEGER PRIMARY KEY, tweet_id TEXT, rating INTEGER, user TEXT, topics TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP)')


def connect():
    conn = sqlite3.connect(db_file)
    return conn


if __name__ == '__main__':
    create_db()
    print('Created DB')
