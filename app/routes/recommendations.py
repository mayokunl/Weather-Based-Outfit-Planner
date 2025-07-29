from flask import Blueprint, render_template, session, flash, redirect, url_for
import markdown
from flask_login import current_user, login_required
from app.services.weather_service import get_weather_summary
from app.services.genai_service import build_prompt_from_session, get_recommendations
from app.services.serp_service import get_overall_outfit_image, get_shopping_items
from app.services.database_service import add_trip_orm, DatabaseError, DatabaseValidationError
from app.services.session_service import TripPlanningSession
from app.utils.helpers import parse_daily_outfits
import logging

logger = logging.getLogger(__name__)

recommendations_bp = Blueprint('recommendations', __name__)

@recommendations_bp.route('/recommendations')
@login_required
def recommendations():
    try:
        print("=== RECOMMENDATIONS ROUTE DEBUG ===")
        print(f"Session data: {dict(session)}")
        
        # Get user profile data
        user_profile = TripPlanningSession.get_user_profile()
        
        # Get trip data from session
        trip_data = TripPlanningSession.get_trip_data()
        print(f"Trip data from session service: {trip_data}")
        
        if not trip_data:
            flash('No trip data found. Please start a new trip.', 'error')
            return redirect(url_for('main.destination'))
        
        # Check if all required data is present
        required_fields = ['city', 'start_date', 'end_date', 'days', 'activities']
        missing_fields = [field for field in required_fields if field not in trip_data]
        
        if missing_fields:
            flash(f'Missing information: {", ".join(missing_fields)}. Please complete your trip planning.', 'error')
            return redirect(url_for('main.destination'))
        
        print("All required session data present, proceeding with recommendations...")

        # Prepare template data
        template_data = {
            'city': trip_data['city'],
            'region': trip_data['region'],
            'start_date': trip_data['start_date'],
            'end_date': trip_data['end_date'],
            'days': trip_data['days'],
            'activities': trip_data['activities'],
            'weather_summary': trip_data.get('weather_summary', 'Weather data not available'),
            'gender': user_profile.get('gender', 'unisex'),
            'age': user_profile.get('age', 'N/A')
        }
        
        print(f"Template data being passed: {template_data}")
        
        # Get the AI response from session, but clean it completely
        response = "Basic outfit recommendations for your trip - dress appropriately for the weather and activities."
        
        print(f"Response being passed: {response[:100] if response else 'No response'}...")

        return render_template('recommendations.html', data=template_data, response=response)
    
    except Exception as e:
        logger.error(f"Error generating recommendations: {e}")
        print(f"ERROR in recommendations route: {e}")
        flash('An error occurred while generating recommendations. Please try again.', 'error')
        return redirect(url_for('main.destination'))
