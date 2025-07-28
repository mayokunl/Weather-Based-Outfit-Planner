"""
Database service using Flask-SQLAlchemy ORM with comprehensive error handling.
Replaces legacy raw SQL operations with proper ORM methods.
"""
from app import db
from app.models.user import User
from app.models.trip import Trip
from app.models.closet import ClosetItem
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
import logging

# Configure logging
logger = logging.getLogger(__name__)

class DatabaseError(Exception):
    """Custom exception for database operations."""
    pass

class DatabaseValidationError(Exception):
    """Custom exception for database validation errors."""
    pass

def add_trip_orm(user_id, city, region, gender=None, age=None, activities=None, duration=None, weather=None, recommendations=None):
    """Add a trip using Flask-SQLAlchemy ORM with error handling."""
    try:
        # Validate user exists
        user = User.query.get(user_id)
        if not user:
            raise DatabaseValidationError(f"User with ID {user_id} not found")
        
        # Validate required fields
        if not city or not region:
            raise DatabaseValidationError("City and region are required fields")
        
        trip = Trip(
            user_id=user_id,
            city=city,
            region=region,
            gender=gender,
            age=age,
            activities=activities,
            duration=duration,
            weather=weather,
            recommendations=recommendations
        )
        db.session.add(trip)
        db.session.commit()
        
        logger.info(f"Successfully created trip {trip.id} for user {user_id}")
        return trip.id
        
    except IntegrityError as e:
        db.session.rollback()
        logger.error(f"Integrity error creating trip: {e}")
        raise DatabaseError(f"Failed to create trip: Data integrity violation")
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Database error creating trip: {e}")
        raise DatabaseError(f"Database error: {str(e)}")
    except DatabaseValidationError:
        raise
    except Exception as e:
        db.session.rollback()
        logger.error(f"Unexpected error creating trip: {e}")
        raise DatabaseError(f"Unexpected error: {str(e)}")

def fetch_trips_by_user_orm(user_id):
    """Fetch all trips for a specific user using ORM with error handling."""
    try:
        # Validate user exists
        user = User.query.get(user_id)
        if not user:
            raise DatabaseValidationError(f"User with ID {user_id} not found")
        
        trips = Trip.query.filter_by(user_id=user_id).all()
        
        trips_data = [
            {
                'id': trip.id,
                'city': trip.city,
                'region': trip.region,
                'activities': trip.activities,
                'duration': trip.duration,
                'recommendations': trip.recommendations,
                'weather': trip.weather,
                'gender': trip.gender,
                'age': trip.age
            }
            for trip in trips
        ]
        
        logger.info(f"Successfully fetched {len(trips_data)} trips for user {user_id}")
        return trips_data
        
    except SQLAlchemyError as e:
        logger.error(f"Database error fetching trips for user {user_id}: {e}")
        raise DatabaseError(f"Database error: {str(e)}")
    except DatabaseValidationError:
        raise
    except Exception as e:
        logger.error(f"Unexpected error fetching trips for user {user_id}: {e}")
        raise DatabaseError(f"Unexpected error: {str(e)}")

def get_user_by_email(email):
    """Get user by email using ORM."""
    return User.query.filter_by(email=email).first()

def create_user(username, email, password_hash, name=None, age=None, gender=None):
    """Create a new user using ORM with error handling."""
    try:
        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            raise DatabaseValidationError(f"User with email {email} already exists")
        
        existing_username = User.query.filter_by(username=username).first()
        if existing_username:
            raise DatabaseValidationError(f"Username {username} already taken")
        
        user = User(
            username=username,
            email=email,
            password=password_hash,
            name=name,
            age=age,
            gender=gender
        )
        db.session.add(user)
        db.session.commit()
        
        logger.info(f"Successfully created user {user.id} with username {username}")
        return user
        
    except IntegrityError as e:
        db.session.rollback()
        logger.error(f"Integrity error creating user: {e}")
        raise DatabaseError(f"Failed to create user: Data integrity violation")
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Database error creating user: {e}")
        raise DatabaseError(f"Database error: {str(e)}")
    except DatabaseValidationError:
        raise
    except Exception as e:
        db.session.rollback()
        logger.error(f"Unexpected error creating user: {e}")
        raise DatabaseError(f"Unexpected error: {str(e)}")
