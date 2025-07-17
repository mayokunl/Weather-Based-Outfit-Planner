import sqlalchemy as db
from sqlalchemy import text
from dotenv import load_dotenv
import os

load_dotenv()

engine = db.create_engine('sqlite:///tripstylist.db')

def init_db():
    with engine.connect() as connection:
        # Create users table if missing
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL
            );
        """))

        # Create trips table if missing
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS trips (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                city TEXT NOT NULL,
                region TEXT NOT NULL,
                gender TEXT,
                age INTEGER,
                activities TEXT,
                duration INTEGER,
                weather TEXT,
                recommendations TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id)
            );
        """))

        connection.commit()
