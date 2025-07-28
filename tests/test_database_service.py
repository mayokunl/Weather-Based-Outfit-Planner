"""
Tests for database service functionality.
Tests ORM operations, error handling, and validation.
"""
import unittest
import sys
import os
from unittest.mock import patch, MagicMock, Mock

# Add the parent directory to the path so we can import the app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models.user import User
from app.models.trip import Trip
from app.services.database_service import (
    add_trip_orm, fetch_trips_by_user_orm, create_user,
    DatabaseError, DatabaseValidationError
)

class TestDatabaseService(unittest.TestCase):
    
    def setUp(self):
        """Set up test database and app context."""
        # Set environment variable for testing
        os.environ['FLASK_ENV'] = 'testing'
        
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        
        # Create test user
        self.test_user = User(
            username='testuser',
            email='test@example.com',
            password='hashedpassword',
            name='Test User',
            age=25,
            gender='female'
        )
        db.session.add(self.test_user)
        db.session.commit()
    
    def tearDown(self):
        """Clean up after tests."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_add_trip_orm_success(self):
        """Test successful trip creation."""
        trip_id = add_trip_orm(
            user_id=self.test_user.id,
            city='New York',
            region='NY',
            gender='female',
            age=25,
            activities='shopping,sightseeing',
            duration=3,
            weather='sunny',
            recommendations='Pack light clothes'
        )
        
        self.assertIsNotNone(trip_id)
        trip = Trip.query.get(trip_id)
        self.assertEqual(trip.city, 'New York')
        self.assertEqual(trip.region, 'NY')
        self.assertEqual(trip.user_id, self.test_user.id)
    
    def test_add_trip_orm_invalid_user(self):
        """Test trip creation with invalid user ID."""
        with self.assertRaises(DatabaseValidationError):
            add_trip_orm(
                user_id=999,  # Non-existent user
                city='New York',
                region='NY'
            )
    
    def test_add_trip_orm_missing_required_fields(self):
        """Test trip creation with missing required fields."""
        with self.assertRaises(DatabaseValidationError):
            add_trip_orm(
                user_id=self.test_user.id,
                city='',  # Empty city
                region='NY'
            )
    
    def test_fetch_trips_by_user_orm_success(self):
        """Test successful trip retrieval."""
        # Create test trip
        trip_id = add_trip_orm(
            user_id=self.test_user.id,
            city='Paris',
            region='France',
            duration=5
        )
        
        trips = fetch_trips_by_user_orm(self.test_user.id)
        
        self.assertEqual(len(trips), 1)
        self.assertEqual(trips[0]['city'], 'Paris')
        self.assertEqual(trips[0]['region'], 'France')
        self.assertEqual(trips[0]['duration'], 5)
    
    def test_fetch_trips_by_user_orm_invalid_user(self):
        """Test trip retrieval with invalid user ID."""
        with self.assertRaises(DatabaseValidationError):
            fetch_trips_by_user_orm(999)  # Non-existent user
    
    def test_create_user_success(self):
        """Test successful user creation."""
        user = create_user(
            username='newuser',
            email='new@example.com',
            password_hash='hashedpw',
            name='New User',
            age=30,
            gender='male'
        )
        
        self.assertIsNotNone(user.id)
        self.assertEqual(user.username, 'newuser')
        self.assertEqual(user.email, 'new@example.com')
    
    def test_create_user_duplicate_email(self):
        """Test user creation with duplicate email."""
        with self.assertRaises(DatabaseValidationError):
            create_user(
                username='anotheruser',
                email='test@example.com',  # Already exists
                password_hash='hashedpw'
            )
    
    def test_create_user_duplicate_username(self):
        """Test user creation with duplicate username."""
        with self.assertRaises(DatabaseValidationError):
            create_user(
                username='testuser',  # Already exists
                email='different@example.com',
                password_hash='hashedpw'
            )

class TestDatabaseServiceErrorHandling(unittest.TestCase):
    """Test error handling in database service."""
    
    def setUp(self):
        """Set up test app context."""
        # Set environment variable for testing
        os.environ['FLASK_ENV'] = 'testing'
        
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
    
    def tearDown(self):
        """Clean up after tests."""
        self.app_context.pop()
    
    @patch('app.services.database_service.db.session.commit')
    @patch('app.services.database_service.User.query')
    def test_add_trip_orm_database_error(self, mock_user_query, mock_commit):
        """Test database error handling in add_trip_orm."""
        # Mock user exists but commit fails
        mock_user = Mock()
        mock_user_query.get.return_value = mock_user
        mock_commit.side_effect = Exception("Database connection failed")
        
        with self.assertRaises(DatabaseError):
            add_trip_orm(
                user_id=1,
                city='Test City',
                region='Test Region'
            )
    
    @patch('app.services.database_service.Trip.query')
    @patch('app.services.database_service.User.query')
    def test_fetch_trips_database_error(self, mock_user_query, mock_trip_query):
        """Test database error handling in fetch_trips_by_user_orm."""
        # Mock user exists but query fails
        mock_user = Mock()
        mock_user_query.get.return_value = mock_user
        mock_trip_query.filter_by.side_effect = Exception("Query failed")
        
        with self.assertRaises(DatabaseError):
            fetch_trips_by_user_orm(1)

if __name__ == '__main__':
    unittest.main()
