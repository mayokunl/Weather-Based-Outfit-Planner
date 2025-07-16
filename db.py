import sqlalchemy as db

engine = db.create_engine('sqlite:///tripstylist.db')

def init_db():
    with engine.connect() as connection:
        #Create users table
        connection.execute(db.text("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL
            );
        """))

        #Create trips table
        connection.execute(db.text("""
            CREATE TABLE IF NOT EXISTS trips (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                location TEXT NOT NULL,
                gender TEXT NOT NULL,
                age INTEGER,
                activities TEXT NOT NULL,
                duration INTEGER NOT NULL,
                weather TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id)
            );
        """))
        connection.commit()