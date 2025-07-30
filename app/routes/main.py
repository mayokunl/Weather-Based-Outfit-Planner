from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify, abort
from flask_login import login_required, current_user
from app import db
from app.services.database_service import fetch_trips_by_user_orm, delete_trip_orm, get_trip_by_id_orm

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

        # Debugging messages
        print(f"City: {city}, Region: {region}")

        # Basic validation
        if not city or not region:
            flash('Both city and region are required', 'error')
            return render_template('destination.html')

        # Store in session for now
        session['city'] = city
        session['region'] = region

        # Debugging messages
        print("Redirecting to duration...")
        return redirect(url_for('main.duration'))

    return render_template('destination.html')

@main_bp.route('/duration', methods=['GET', 'POST'])
@login_required
def duration():
    if request.method == 'POST':
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        activities = request.form.getlist('activities')  # Get list of activities
        
        if not start_date or not end_date:
            flash('Both start and end dates are required', 'error')
            return render_template('duration.html')
        
        # Store in session
        session['start_date'] = start_date
        session['end_date'] = end_date
        session['activities'] = activities
        
        # Calculate and store days
        from datetime import datetime
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d')
            end = datetime.strptime(end_date, '%Y-%m-%d')
            days = (end - start).days + 1
            session['days'] = days
        except Exception:
            session['days'] = None
        
        print(f"Duration route - storing session data:")
        print(f"  Start: {start_date}, End: {end_date}")
        print(f"  Activities: {activities}")
        print(f"  Days: {session.get('days')}")
        
        # Redirect to recommendations
        return redirect(url_for('recommendations.recommendations'))
    
    return render_template('duration.html')

@main_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        name = request.form.get('name')
        age = request.form.get('age')
        gender = request.form.get('gender')

        current_user.name = name
        current_user.age = age
        current_user.gender = gender

        db.session.commit()
        flash('Profile updated successfully!', 'success')

        return redirect(url_for('main.profile'))

    # Fetch user's trips for display
    try:
        trips_data = fetch_trips_by_user_orm(current_user.id)
        trips_to_show = []
        for trip in trips_data:
            location = trip['city']
            if trip.get('region'):
                location += f", {trip['region']}"
            trips_to_show.append({
                'id': trip['id'],
                'location': location,
                'activities': trip['activities'].split(',') if trip['activities'] else [],
                'duration': trip['duration'],
                'recommendations': trip['recommendations']
            })
    except Exception as e:
        print(f"Error fetching trips: {e}")
        trips_to_show = []

    return render_template('profile.html', user=current_user, trips=trips_to_show)

@main_bp.route('/trip/<int:trip_id>/delete', methods=['POST'])
@login_required
def delete_trip(trip_id):
    """Delete a trip after confirming user has access"""
    try:
        # Check if trip exists and belongs to user
        trip = get_trip_by_id_orm(trip_id, current_user.id)
        if not trip:
            flash('Trip not found or you do not have permission to delete it.', 'error')
            return redirect(url_for('main.profile'))
        
        # Delete the trip
        if delete_trip_orm(trip_id, current_user.id):
            flash('Trip deleted successfully!', 'success')
        else:
            flash('Error deleting trip. Please try again.', 'error')
    except Exception as e:
        print(f"Error deleting trip {trip_id}: {e}")
        flash('An unexpected error occurred. Please try again.', 'error')
    
    return redirect(url_for('main.profile'))

@main_bp.route('/trip/<int:trip_id>/view')
@login_required  
def view_trip(trip_id):
    """View complete trip recommendations"""
    try:
        # Get trip details
        trip = get_trip_by_id_orm(trip_id, current_user.id)
        if not trip:
            flash('Trip not found or you do not have permission to view it.', 'error')
            return redirect(url_for('main.profile'))

        # Get outfit data if available - use the model's method
        outfit_data = trip.get_outfit_data() if hasattr(trip, 'get_outfit_data') else {}
        # If outfit_data is a list (legacy), wrap in dict for compatibility
        if isinstance(outfit_data, list):
            outfit_data = {'days': outfit_data}

        # Get days from outfit_data if available
        days = outfit_data.get('days', []) if isinstance(outfit_data, dict) else []
        # Debug: print shopping data for each day
        for d in days:
            key = d.get('title')
            shopping = outfit_data.get('outfit_data', {}).get(key, {}).get('shopping')
            print(f"[DEBUG] Shopping for '{key}': {shopping}")
        # Get trip details
        trip = get_trip_by_id_orm(trip_id, current_user.id)
        if not trip:
            flash('Trip not found or you do not have permission to view it.', 'error')
            return redirect(url_for('main.profile'))
        
        # Get outfit data if available - use the model's method
        outfit_data = trip.get_outfit_data() if hasattr(trip, 'get_outfit_data') else {}
        # If outfit_data is a list (legacy), wrap in dict for compatibility
        if isinstance(outfit_data, list):
            outfit_data = {'days': outfit_data}

        # Prepare location string
        location = trip.city
        if trip.region:
            location += f", {trip.region}"

        # Clean and split activities for template
        activities_list = [a.strip() for a in trip.activities.split(',')] if trip.activities else []
        activities_list = [a for a in activities_list if a]

        # Get days from outfit_data if available
        days = outfit_data.get('days', []) if isinstance(outfit_data, dict) else []

        # Debug: print keys in outfit_data['outfit_data'] and day titles
        debug_outfit_keys = []
        if isinstance(outfit_data, dict) and 'outfit_data' in outfit_data and isinstance(outfit_data['outfit_data'], dict):
            debug_outfit_keys = list(outfit_data['outfit_data'].keys())
        debug_day_titles = [d.get('title') for d in days]
        print(f"[DEBUG] outfit_data['outfit_data'] keys: {debug_outfit_keys}")
        print(f"[DEBUG] days titles: {debug_day_titles}")

        # Prepare template context
        context = {
            'trip': {
                'id': trip.id,
                'city': trip.city,
                'region': trip.region,
                'duration': trip.duration,
                'activities': trip.activities,
                'recommendations': trip.recommendations
            },
            'location': location,
            'activities': activities_list,
            'outfit_data': outfit_data,
            'days': days,
            'overall_outfit_image': outfit_data.get('overall_outfit_image', '') if isinstance(outfit_data, dict) else '',
            'shopping_items': outfit_data.get('shopping_items', []) if isinstance(outfit_data, dict) else []
        }

        return render_template('trip_details.html', **context)
        
    except Exception as e:
        print(f"Error viewing trip {trip_id}: {e}")
        flash('An unexpected error occurred. Please try again.', 'error')
        return redirect(url_for('main.profile'))