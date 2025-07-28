from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from flask_login import login_required, current_user
from datetime import datetime
from app.services.database_service import fetch_trips_by_user_orm, DatabaseError, DatabaseValidationError
from app.schemas import TripSchema, validate_request_data
from app.services.session_service import TripPlanningSession
import logging

logger = logging.getLogger(__name__)

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@main_bp.route('/home')
def home():
    return render_template('home.html')

@main_bp.route('/destination', methods=['GET', 'POST'])
@login_required
def destination():
    if request.method == 'POST':
        # Get form data  
        city = request.form.get('city', '').strip()
        region = request.form.get('region', '').strip()
        
        # Basic validation
        if not city or not region:
            flash('Both city and region are required', 'error')
            return render_template('destination.html')
        
        # Store data using session service
        TripPlanningSession.set_destination(city, region)
        
        logger.info(f"User {current_user.id} set destination: {city}, {region}")
        return redirect(url_for('main.duration'))
    
    return render_template('destination.html')

@main_bp.route('/duration', methods=['GET', 'POST'])
@login_required
def duration():
    if request.method == 'POST':
        # Get current session data for validation
        trip_data = TripPlanningSession.get_trip_data()
        
        # Add form data to validation
        form_data = {
            'city': trip_data['city'],
            'region': trip_data['region'],
            'start_date': request.form.get('start_date'),
            'end_date': request.form.get('end_date'),
            'activities': request.form.getlist('activities')
        }
        
        # Validate using TripSchema
        validated_data, errors = validate_request_data(TripSchema, form_data)
        
        if errors:
            for field, messages in errors.items():
                for message in messages:
                    flash(f"{field.replace('_', ' ').title()}: {message}", 'error')
            return render_template('duration.html')
        
        # Store validated data using session service
        start_date = validated_data['start_date']
        end_date = validated_data['end_date']
        TripPlanningSession.set_dates(start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
        TripPlanningSession.set_activities(validated_data['activities'])
        
        logger.info(f"User {current_user.id} set duration: {(end_date - start_date).days + 1} days with activities: {validated_data['activities']}")
        return redirect(url_for('recommendations.recommendations'))
    
    return render_template('duration.html')

@main_bp.route('/trips')
@login_required
def trips():
    try:
        trips_data = fetch_trips_by_user_orm(current_user.id)
        trips_to_show = []
        
        for trip in trips_data:
            location = trip['city']
            if trip.get('region'):
                location += f", {trip['region']}"
            trips_to_show.append({
                'location': location,
                'activities': trip['activities'],
                'duration': trip['duration'],
                'recommendations': trip['recommendations']
            })

        logger.info(f"Successfully loaded {len(trips_to_show)} trips for user {current_user.id}")
        return render_template('trips.html', trips=trips_to_show)
        
    except (DatabaseError, DatabaseValidationError) as e:
        logger.error(f"Database error loading trips for user {current_user.id}: {e}")
        flash('Unable to load your trips at this time. Please try again later.', 'error')
        return render_template('trips.html', trips=[])
    except Exception as e:
        logger.error(f"Unexpected error loading trips for user {current_user.id}: {e}")
        flash('An unexpected error occurred. Please try again later.', 'error')
        return render_template('trips.html', trips=[])
