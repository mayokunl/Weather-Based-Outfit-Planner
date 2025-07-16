from db import engine
import sqlalchemy as db

def add_user(username, email):
    insert_sql = "INSERT INTO users (username, email) VALUES (:username, :email)"
    with engine.connect() as connection:
        result = connection.execute(db.text(insert_sql), {"username": username, "email": email})
        connection.commit()
        return result.lastrowid

def add_trip(user_id, location, gender, age, activities, duration, weather):
    insert_sql = """
        INSERT INTO trips (user_id, location, gender, age, activities, duration, weather)
        VALUES (:user_id, :location, :gender, :age, :activities, :duration, :weather)
    """
    with engine.connect() as connection:
        result = connection.execute(db.text(insert_sql), {
            "user_id": user_id,
            "location": location,
            "gender": gender,
            "age": age,
            "activities": activities,
            "duration": duration,
            "weather": weather
        })
        connection.commit()
        return result.lastrowid

def fetch_trips_by_user(user_id):
    query = """
        SELECT id, location, gender, age, activities, duration, weather
        FROM trips WHERE user_id = :user_id
    """
    with engine.connect() as connection:
        result = connection.execute(db.text(query), {"user_id": user_id})
        return [dict(row._mapping) for row in result.fetchall()]

def clear_all_trips():
    with engine.connect() as connection:
        connection.execute(db.text("DELETE FROM trips"))
        connection.commit()

def clear_all_users():
    with engine.connect() as connection:
        connection.execute(db.text("DELETE FROM users"))
        connection.commit()
