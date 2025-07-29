from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from flask_login import login_required, current_user
from app import db
from app.services.database_service import fetch_trips_by_user_orm

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
        
        if not start_date or not end_date:
            flash('Both start and end dates are required', 'error')
            return render_template('duration.html')
        
        # Store in session
        session['start_date'] = start_date
        session['end_date'] = end_date
        
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
                'location': location,
                'activities': trip['activities'].split(',') if trip['activities'] else [],
                'duration': trip['duration'],
                'recommendations': trip['recommendations']
            })
    except Exception as e:
        print(f"Error fetching trips: {e}")
        trips_to_show = []

    return render_template('profile.html', user=current_user, trips=trips_to_show)