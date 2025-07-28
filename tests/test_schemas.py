"""
Tests for marshmallow schemas and validation.
Tests input validation, serialization, and error handling.
"""
import unittest
import sys
import os
from datetime import date, timedelta

# Add the parent directory to the path so we can import the app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.schemas import (
    UserRegistrationSchema, TripSchema, ClosetItemSchema,
    validate_request_data
)
from marshmallow import ValidationError

class TestUserSchemas(unittest.TestCase):
    """Test user-related schemas."""
    
    def test_user_registration_schema_valid(self):
        """Test valid user registration data."""
        data = {
            'username': 'testuser123',
            'email': 'test@example.com',
            'password': 'securepassword',
            'confirm_password': 'securepassword'
        }
        
        validated_data, errors = validate_request_data(UserRegistrationSchema, data)
        
        self.assertIsNotNone(validated_data)
        self.assertIsNone(errors)
        self.assertEqual(validated_data['username'], 'testuser123')
        self.assertEqual(validated_data['email'], 'test@example.com')
    
    def test_user_registration_schema_invalid_email(self):
        """Test user registration with invalid email."""
        data = {
            'username': 'testuser',
            'email': 'invalid-email',
            'password': 'password',
            'confirm_password': 'password'
        }
        
        validated_data, errors = validate_request_data(UserRegistrationSchema, data)
        
        self.assertIsNone(validated_data)
        self.assertIsNotNone(errors)
        self.assertIn('email', errors)
    
    def test_user_registration_schema_password_mismatch(self):
        """Test user registration with password mismatch."""
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'password1',
            'confirm_password': 'password2'
        }
        
        validated_data, errors = validate_request_data(UserRegistrationSchema, data)
        
        self.assertIsNone(validated_data)
        self.assertIsNotNone(errors)
        self.assertIn('confirm_password', errors)
    
    def test_user_registration_schema_short_password(self):
        """Test user registration with short password."""
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': '12345',  # Too short
            'confirm_password': '12345'
        }
        
        validated_data, errors = validate_request_data(UserRegistrationSchema, data)
        
        self.assertIsNone(validated_data)
        self.assertIsNotNone(errors)
        self.assertIn('password', errors)

class TestTripSchemas(unittest.TestCase):
    """Test trip-related schemas."""
    
    def test_trip_schema_valid(self):
        """Test valid trip data."""
        today = date.today()
        tomorrow = today + timedelta(days=1)
        
        data = {
            'city': 'New York',
            'region': 'New York',
            'start_date': today,
            'end_date': tomorrow,
            'activities': ['shopping', 'sightseeing']
        }
        
        validated_data, errors = validate_request_data(TripSchema, data)
        
        self.assertIsNotNone(validated_data)
        self.assertIsNone(errors)
        self.assertEqual(validated_data['city'], 'New York')
        self.assertEqual(validated_data['region'], 'New York')
    
    def test_trip_schema_end_before_start(self):
        """Test trip with end date before start date."""
        today = date.today()
        yesterday = today - timedelta(days=1)
        
        data = {
            'city': 'Paris',
            'region': 'France',
            'start_date': today,
            'end_date': yesterday,  # Before start date
            'activities': []
        }
        
        validated_data, errors = validate_request_data(TripSchema, data)
        
        self.assertIsNone(validated_data)
        self.assertIsNotNone(errors)
        self.assertIn('end_date', errors)

class TestClosetSchema(unittest.TestCase):
    """Test closet item schema."""
    
    def test_closet_item_schema_valid(self):
        """Test valid closet item data."""
        data = {
            'name': 'Blue Jeans',
            'category': 'bottoms',
            'color': 'blue',
            'brand': 'Levi\'s'
        }
        
        validated_data, errors = validate_request_data(ClosetItemSchema, data)
        
        self.assertIsNotNone(validated_data)
        self.assertIsNone(errors)
        self.assertEqual(validated_data['name'], 'Blue Jeans')
        self.assertEqual(validated_data['category'], 'bottoms')
    
    def test_closet_item_schema_invalid_category(self):
        """Test closet item with invalid category."""
        data = {
            'name': 'Blue Jeans',
            'category': 'invalid_category'
        }
        
        validated_data, errors = validate_request_data(ClosetItemSchema, data)
        
        self.assertIsNone(validated_data)
        self.assertIsNotNone(errors)
        self.assertIn('category', errors)

if __name__ == '__main__':
    unittest.main()
