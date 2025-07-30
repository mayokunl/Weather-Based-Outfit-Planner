"""
Unit tests for session_service.py
Tests the TripPlanningSession class methods for session management.
"""
import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
import sys
import os

# Add the parent directory to the path to import the app modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.services.session_service import TripPlanningSession


class TestTripPlanningSession(unittest.TestCase):
    """Test cases for TripPlanningSession class."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.mock_session = {}
        self.mock_user = MagicMock()
        
    def tearDown(self):
        """Clean up after each test method."""
        self.mock_session.clear()

    @patch('app.services.session_service.session')
    def test_set_destination(self, mock_session):
        """Test setting destination information."""
        mock_session.__setitem__ = MagicMock()
        
        TripPlanningSession.set_destination("New York", "NY")
        
        mock_session.__setitem__.assert_any_call('city', 'New York')
        mock_session.__setitem__.assert_any_call('region', 'NY')

    @patch('app.services.session_service.session')
    def test_set_dates_valid(self, mock_session):
        """Test setting valid dates and calculating duration."""
        mock_session.__setitem__ = MagicMock()
        
        start_date = "2025-07-30"
        end_date = "2025-08-05"
        
        TripPlanningSession.set_dates(start_date, end_date)
        
        mock_session.__setitem__.assert_any_call('start_date', start_date)
        mock_session.__setitem__.assert_any_call('end_date', end_date)
        mock_session.__setitem__.assert_any_call('days', 7)  # 6 days difference + 1

    @patch('app.services.session_service.session')
    def test_set_dates_invalid_format(self, mock_session):
        """Test setting dates with invalid format."""
        mock_session.__setitem__ = MagicMock()
        
        start_date = "invalid-date"
        end_date = "2025-08-05"
        
        TripPlanningSession.set_dates(start_date, end_date)
        
        mock_session.__setitem__.assert_any_call('start_date', start_date)
        mock_session.__setitem__.assert_any_call('end_date', end_date)
        mock_session.__setitem__.assert_any_call('days', None)

    @patch('app.services.session_service.session')
    def test_set_dates_same_day(self, mock_session):
        """Test setting same start and end date."""
        mock_session.__setitem__ = MagicMock()
        
        date = "2025-07-30"
        
        TripPlanningSession.set_dates(date, date)
        
        mock_session.__setitem__.assert_any_call('days', 1)

    @patch('app.services.session_service.session')
    def test_set_activities(self, mock_session):
        """Test setting activities list."""
        mock_session.__setitem__ = MagicMock()
        
        activities = ["hiking", "sightseeing", "dining"]
        
        TripPlanningSession.set_activities(activities)
        
        mock_session.__setitem__.assert_called_once_with('activities', activities)

    @patch('app.services.session_service.session')
    def test_set_weather_summary(self, mock_session):
        """Test setting weather summary."""
        mock_session.__setitem__ = MagicMock()
        
        weather = "Sunny, 75°F, light breeze"
        
        TripPlanningSession.set_weather_summary(weather)
        
        mock_session.__setitem__.assert_called_once_with('weather_summary', weather)

    @patch('app.services.session_service.session')
    def test_set_recommendations(self, mock_session):
        """Test setting AI recommendations."""
        mock_session.__setitem__ = MagicMock()
        
        recommendations = "Wear light clothing, bring sunglasses"
        
        TripPlanningSession.set_recommendations(recommendations)
        
        mock_session.__setitem__.assert_called_once_with('recommendations', recommendations)

    @patch('app.services.session_service.current_user')
    @patch('app.services.session_service.session')
    def test_get_user_profile_authenticated(self, mock_session, mock_current_user):
        """Test getting user profile when user is authenticated."""
        mock_current_user.is_authenticated = True
        mock_current_user.gender = "female"
        mock_current_user.age = 25
        mock_current_user.id = 123
        mock_session.get.return_value = "fallback_value"
        
        result = TripPlanningSession.get_user_profile()
        
        expected = {
            'gender': 'female',
            'age': 25,
            'user_id': 123
        }
        self.assertEqual(result, expected)

    @patch('app.services.session_service.current_user')
    @patch('app.services.session_service.session')
    def test_get_user_profile_authenticated_with_none_values(self, mock_session, mock_current_user):
        """Test getting user profile when authenticated user has None values."""
        mock_current_user.is_authenticated = True
        mock_current_user.gender = None
        mock_current_user.age = None
        mock_current_user.id = 123
        mock_session.get.side_effect = lambda key, default=None: {
            'gender': 'male',
            'age': 30
        }.get(key, default)
        
        result = TripPlanningSession.get_user_profile()
        
        expected = {
            'gender': 'male',
            'age': 30,
            'user_id': 123
        }
        self.assertEqual(result, expected)

    @patch('app.services.session_service.current_user')
    @patch('app.services.session_service.session')
    def test_get_user_profile_not_authenticated(self, mock_session, mock_current_user):
        """Test getting user profile when user is not authenticated."""
        mock_current_user.is_authenticated = False
        mock_session.get.side_effect = lambda key, default=None: {
            'gender': 'male',
            'age': 28,
            '_user_id': 456
        }.get(key, default)
        
        result = TripPlanningSession.get_user_profile()
        
        expected = {
            'gender': 'male',
            'age': 28,
            'user_id': 456
        }
        self.assertEqual(result, expected)

    @patch('app.services.session_service.current_user')
    @patch('app.services.session_service.session')
    def test_get_user_profile_not_authenticated_defaults(self, mock_session, mock_current_user):
        """Test getting user profile with default values when not authenticated."""
        mock_current_user.is_authenticated = False
        mock_session.get.side_effect = lambda key, default=None: default
        
        result = TripPlanningSession.get_user_profile()
        
        expected = {
            'gender': 'unisex',
            'age': None,
            'user_id': None
        }
        self.assertEqual(result, expected)

    @patch('app.services.session_service.session')
    def test_get_trip_data(self, mock_session):
        """Test getting all trip data from session."""
        mock_session.get.side_effect = lambda key, default=None: {
            'city': 'Paris',
            'region': 'France',
            'start_date': '2025-08-01',
            'end_date': '2025-08-07',
            'days': 7,
            'activities': ['museums', 'restaurants'],
            'weather_summary': 'Warm and sunny',
            'recommendations': 'Pack light clothes'
        }.get(key, default)
        
        result = TripPlanningSession.get_trip_data()
        
        expected = {
            'city': 'Paris',
            'region': 'France',
            'start_date': '2025-08-01',
            'end_date': '2025-08-07',
            'days': 7,
            'activities': ['museums', 'restaurants'],
            'weather_summary': 'Warm and sunny',
            'recommendations': 'Pack light clothes'
        }
        self.assertEqual(result, expected)

    @patch('app.services.session_service.session')
    def test_get_trip_data_empty_session(self, mock_session):
        """Test getting trip data when session is empty."""
        mock_session.get.side_effect = lambda key, default=None: [] if key == 'activities' else default
        
        result = TripPlanningSession.get_trip_data()
        
        expected = {
            'city': None,
            'region': None,
            'start_date': None,
            'end_date': None,
            'days': None,
            'activities': [],
            'weather_summary': None,
            'recommendations': None
        }
        self.assertEqual(result, expected)

    @patch('app.services.session_service.session')
    def test_clear_trip_data(self, mock_session):
        """Test clearing all trip data from session."""
        mock_session.pop = MagicMock()
        
        TripPlanningSession.clear_trip_data()
        
        expected_keys = [
            'city', 'region', 'start_date', 'end_date', 'days',
            'activities', 'weather_summary', 'recommendations'
        ]
        
        self.assertEqual(mock_session.pop.call_count, len(expected_keys))
        
        for key in expected_keys:
            mock_session.pop.assert_any_call(key, None)

    @patch('app.services.session_service.session')
    def test_clear_recommendations(self, mock_session):
        """Test clearing only recommendations from session."""
        mock_session.pop = MagicMock()
        
        TripPlanningSession.clear_recommendations()
        
        mock_session.pop.assert_called_once_with('recommendations', None)

    def test_date_calculation_edge_cases(self):
        """Test date calculation with various edge cases."""
        with patch('app.services.session_service.session') as mock_session:
            mock_session.__setitem__ = MagicMock()
            
            # Test leap year
            TripPlanningSession.set_dates("2024-02-28", "2024-03-01")
            mock_session.__setitem__.assert_any_call('days', 3)  # Feb 29 exists in 2024
            
            # Test year boundary
            TripPlanningSession.set_dates("2024-12-31", "2025-01-02")
            mock_session.__setitem__.assert_any_call('days', 3)
            
            # Test same month
            TripPlanningSession.set_dates("2025-07-15", "2025-07-20")
            mock_session.__setitem__.assert_any_call('days', 6)

    @patch('app.services.session_service.session')
    def test_set_activities_empty_list(self, mock_session):
        """Test setting empty activities list."""
        mock_session.__setitem__ = MagicMock()
        
        TripPlanningSession.set_activities([])
        
        mock_session.__setitem__.assert_called_once_with('activities', [])

    @patch('app.services.session_service.session')
    def test_set_activities_none(self, mock_session):
        """Test setting activities to None."""
        mock_session.__setitem__ = MagicMock()
        
        TripPlanningSession.set_activities(None)
        
        mock_session.__setitem__.assert_called_once_with('activities', None)

    def test_all_methods_are_static(self):
        """Test that all methods are static methods."""
        methods = [
            'set_destination', 'set_dates', 'set_activities', 'set_weather_summary',
            'set_recommendations', 'get_user_profile', 'get_trip_data',
            'clear_trip_data', 'clear_recommendations'
        ]
        
        for method_name in methods:
            method = getattr(TripPlanningSession, method_name)
            self.assertTrue(isinstance(method, staticmethod) or 
                          hasattr(method, '__func__'),
                          f"{method_name} should be a static method")


class TestIntegrationScenarios(unittest.TestCase):
    """Integration test scenarios for typical user workflows."""
    
    @patch('app.services.session_service.current_user')
    @patch('app.services.session_service.session')
    def test_complete_trip_planning_workflow(self, mock_session, mock_current_user):
        """Test a complete trip planning workflow."""
        # Mock session storage
        session_data = {}
        
        def set_item(key, value):
            session_data[key] = value
            
        def get_item(key, default=None):
            return session_data.get(key, default)
            
        mock_session.__setitem__ = set_item
        mock_session.get = get_item
        
        # Mock authenticated user
        mock_current_user.is_authenticated = True
        mock_current_user.gender = "female"
        mock_current_user.age = 30
        mock_current_user.id = 789
        
        # Step 1: Set destination
        TripPlanningSession.set_destination("Tokyo", "Japan")
        
        # Step 2: Set dates
        TripPlanningSession.set_dates("2025-09-01", "2025-09-05")
        
        # Step 3: Set activities
        TripPlanningSession.set_activities(["temples", "shopping", "dining"])
        
        # Step 4: Set weather summary
        TripPlanningSession.set_weather_summary("Mild temperatures, occasional rain")
        
        # Step 5: Set recommendations
        TripPlanningSession.set_recommendations("Bring umbrella and comfortable shoes")
        
        # Verify all data is stored correctly
        trip_data = TripPlanningSession.get_trip_data()
        user_profile = TripPlanningSession.get_user_profile()
        
        expected_trip_data = {
            'city': 'Tokyo',
            'region': 'Japan',
            'start_date': '2025-09-01',
            'end_date': '2025-09-05',
            'days': 5,
            'activities': ['temples', 'shopping', 'dining'],
            'weather_summary': 'Mild temperatures, occasional rain',
            'recommendations': 'Bring umbrella and comfortable shoes'
        }
        
        expected_user_profile = {
            'gender': 'female',
            'age': 30,
            'user_id': 789
        }
        
        self.assertEqual(trip_data, expected_trip_data)
        self.assertEqual(user_profile, expected_user_profile)
        
        # Test clearing recommendations only
        TripPlanningSession.clear_recommendations()
        updated_trip_data = TripPlanningSession.get_trip_data()
        self.assertIsNone(updated_trip_data['recommendations'])
        self.assertEqual(updated_trip_data['city'], 'Tokyo')  # Other data should remain
        
        # Test clearing all trip data
        TripPlanningSession.clear_trip_data()
        cleared_trip_data = TripPlanningSession.get_trip_data()
        
        expected_cleared_data = {
            'city': None,
            'region': None,
            'start_date': None,
            'end_date': None,
            'days': None,
            'activities': [],
            'weather_summary': None,
            'recommendations': None
        }
        
        self.assertEqual(cleared_trip_data, expected_cleared_data)


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)
