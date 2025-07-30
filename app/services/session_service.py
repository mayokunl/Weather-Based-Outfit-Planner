"""
Session management service for trip planning workflow.
Centralizes session data handling to avoid repetition.
"""
from flask import session
from flask_login import current_user

class TripPlanningSession:
    """Manages session data for trip planning workflow."""
    
    @staticmethod
    def set_destination(city, region):
        """Store destination information."""
        session['city'] = city
        session['region'] = region
    
    @staticmethod
    def set_dates(start_date, end_date):
        """Store trip dates and calculate duration."""
        from datetime import datetime
        session['start_date'] = start_date
        session['end_date'] = end_date
        
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d')
            end = datetime.strptime(end_date, '%Y-%m-%d')
            days = (end - start).days + 1
        except Exception:
            days = None
        session['days'] = days
    
    @staticmethod
    def set_activities(activities):
        """Store selected activities."""
        session['activities'] = activities
    
    @staticmethod
    def set_weather_summary(weather_summary):
        """Store weather information."""
        session['weather_summary'] = weather_summary
    
    @staticmethod
    def set_recommendations(recommendations):
        """Store AI-generated recommendations."""
        session['recommendations'] = recommendations
    
    @staticmethod
    def get_user_profile():
        """Get user profile data from current_user or session fallback."""
        if current_user.is_authenticated:
            return {
                'gender': current_user.gender or session.get('gender', 'unisex'),
                'age': current_user.age or session.get('age'),
                'user_id': current_user.id
            }
        return {
            'gender': session.get('gender', 'unisex'),
            'age': session.get('age'),
            'user_id': session.get('_user_id')
        }
    
    @staticmethod
    def get_trip_data():
        """Get all trip-related session data."""
        return {
            'city': session.get('city'),
            'region': session.get('region'),
            'start_date': session.get('start_date'),
            'end_date': session.get('end_date'),
            'days': session.get('days'),
            'activities': session.get('activities', []),
            'weather_summary': session.get('weather_summary'),
            'recommendations': session.get('recommendations')
        }
    
    @staticmethod
    def clear_trip_data():
        """Clear trip planning session data."""
        keys_to_clear = [
            'city', 'region', 'start_date', 'end_date', 'days',
            'activities', 'weather_summary', 'recommendations'
        ]
        for key in keys_to_clear:
            session.pop(key, None)

    @staticmethod
    def clear_recommendations():
        """Clear only the recommendations from session."""
        session.pop('recommendations', None)