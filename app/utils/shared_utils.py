"""
Shared utilities and decorators for reducing code duplication.
"""
import logging
from functools import wraps
from flask import flash
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from app import db
from app.services.database_service import DatabaseError, DatabaseValidationError

logger = logging.getLogger(__name__)

def handle_database_errors(operation_name="database operation"):
    """
    Decorator to handle common database error patterns.
    
    Args:
        operation_name (str): Description of the operation for logging
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except IntegrityError as e:
                db.session.rollback()
                logger.error(f"Integrity error in {operation_name}: {e}")
                raise DatabaseError(f"Failed to {operation_name}: Data integrity violation")
            except SQLAlchemyError as e:
                db.session.rollback()
                logger.error(f"Database error in {operation_name}: {e}")
                raise DatabaseError(f"Database error: {str(e)}")
            except DatabaseValidationError:
                raise
            except Exception as e:
                db.session.rollback()
                logger.error(f"Unexpected error in {operation_name}: {e}")
                raise DatabaseError(f"Unexpected error: {str(e)}")
        return wrapper
    return decorator

def handle_route_errors(success_message=None, error_redirect=None):
    """
    Decorator to handle common route error patterns with flash messages.
    
    Args:
        success_message (str): Message to flash on success
        error_redirect (str): Route to redirect to on error
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                if success_message:
                    flash(success_message, 'success')
                return result
            except DatabaseValidationError as e:
                flash(str(e), 'error')
                logger.error(f"Validation error in {func.__name__}: {e}")
                if error_redirect:
                    from flask import redirect, url_for
                    return redirect(url_for(error_redirect))
                raise
            except DatabaseError as e:
                flash('A database error occurred. Please try again.', 'error')
                logger.error(f"Database error in {func.__name__}: {e}")
                if error_redirect:
                    from flask import redirect, url_for
                    return redirect(url_for(error_redirect))
                raise
            except Exception as e:
                flash('An unexpected error occurred. Please try again.', 'error')
                logger.error(f"Unexpected error in {func.__name__}: {e}")
                if error_redirect:
                    from flask import redirect, url_for
                    return redirect(url_for(error_redirect))
                raise
        return wrapper
    return decorator

def log_user_action(action_description):
    """
    Decorator to log user actions consistently.
    
    Args:
        action_description (str): Description of the action being performed
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            from flask_login import current_user
            
            # Log action start
            user_info = f"user {current_user.id}" if current_user.is_authenticated else "anonymous user"
            logger.info(f"{user_info} started {action_description}")
            
            try:
                result = func(*args, **kwargs)
                logger.info(f"{user_info} successfully completed {action_description}")
                return result
            except Exception as e:
                logger.error(f"{user_info} failed {action_description}: {e}")
                raise
        return wrapper
    return decorator

class ErrorMessages:
    """Centralized error messages to avoid duplication."""
    
    # Database errors
    DB_CONNECTION_ERROR = "Unable to connect to the database. Please try again later."
    DB_INTEGRITY_ERROR = "Data validation failed. Please check your input."
    DB_GENERIC_ERROR = "A database error occurred. Please try again."
    
    # Validation errors
    REQUIRED_FIELDS = "All required fields must be filled out."
    INVALID_DATE_RANGE = "End date must be after start date."
    INVALID_EMAIL = "Please enter a valid email address."
    PASSWORD_MISMATCH = "Passwords do not match."
    PASSWORD_TOO_SHORT = "Password must be at least 6 characters long."
    
    # User/Auth errors
    USER_NOT_FOUND = "User not found."
    INVALID_CREDENTIALS = "Invalid email or password."
    USER_EXISTS = "A user with this email already exists."
    LOGIN_REQUIRED = "Please log in to access this page."
    
    # Trip/Session errors
    TRIP_DATA_MISSING = "Missing trip information. Please start planning your trip again."
    WEATHER_API_ERROR = "Unable to fetch weather data. Please try again."
    RECOMMENDATION_ERROR = "Unable to generate recommendations. Please try again."
    
    # Generic errors
    UNEXPECTED_ERROR = "An unexpected error occurred. Please try again."
    FILE_UPLOAD_ERROR = "File upload failed. Please try again."
    NETWORK_ERROR = "Network error. Please check your connection."

class SuccessMessages:
    """Centralized success messages to avoid duplication."""
    
    # User actions
    USER_REGISTERED = "Account created successfully! Welcome!"
    USER_LOGGED_IN = "Logged in successfully!"
    USER_LOGGED_OUT = "Logged out successfully!"
    PROFILE_UPDATED = "Profile updated successfully!"
    
    # Trip actions
    TRIP_SAVED = "Trip saved successfully!"
    DESTINATION_SET = "Destination set successfully!"
    DURATION_SET = "Trip duration and activities set successfully!"
    
    # Closet actions
    ITEM_ADDED = "Item added to your closet!"
    ITEM_REMOVED = "Item removed from your closet!"
    
    # Generic
    OPERATION_SUCCESS = "Operation completed successfully!"
