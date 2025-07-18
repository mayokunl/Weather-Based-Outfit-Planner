import sqlalchemy as db
from sqlalchemy import text
from db import engine 

def add_user(username, email):
    select_sql = "SELECT id FROM users WHERE email = :email"
    with engine.connect() as connection:
        result = connection.execute(db.text(select_sql), {"email": email}).fetchone()
        if result:
            # user exists, return existing id
            return result[0]
        # else insert new user
        insert_sql = "INSERT INTO users (username, email) VALUES (:username, :email)"
        res = connection.execute(db.text(insert_sql), {"username": username, "email": email})
        connection.commit()
        return res.lastrowid


def add_trip(user_id, city, region, gender, age, activities, duration, weather, recommendations=None):
    insert_sql = """
    INSERT INTO trips (user_id, city, region, gender, age, activities, duration, weather, recommendations)
    VALUES (:user_id, :city, :region, :gender, :age, :activities, :duration, :weather, :recommendations)
    """
    with engine.begin() as connection:
        connection.execute(text(insert_sql), {
            "user_id": user_id,
            "city": city,
            "region": region,
            "gender": gender,
            "age": age,
            "activities": activities,
            "duration": duration,
            "weather": weather,
            "recommendations": recommendations
        })

def fetch_trips_by_user(user_id):
    query = """
        SELECT id, city, region, activities, duration, recommendations
        FROM trips
        WHERE user_id = :user_id
    """
    with engine.connect() as connection:
        result = connection.execute(text(query), {"user_id": user_id})
        trips = [dict(row._mapping) for row in result]
    return trips

