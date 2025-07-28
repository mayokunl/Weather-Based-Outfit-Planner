from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from flask_login import login_required, current_user
from datetime import datetime
from app.database.db_utils import fetch_trips_by_user

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@main_bp.route('/home')
def home():
    return render_template('home.html')

@main_bp.route('/destination', methods=['GET', 'POST'])
@login_required
def destination():
    if request.method == 'POST':
        session['city'] = request.form.get('city', '')
        session['region'] = request.form.get('region', '')
        return redirect(url_for('main.duration'))
    return render_template('destination.html')

@main_bp.route('/duration', methods=['GET', 'POST'])
def duration():
    if request.method == 'POST':
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        session['start_date'] = start_date
        session['end_date'] = end_date

        try:
            start = datetime.strptime(start_date, '%Y-%m-%d')
            end = datetime.strptime(end_date, '%Y-%m-%d')
            days = (end - start).days + 1
        except Exception:
            days = None
        session['days'] = days

        activities = request.form.getlist('activities')
        session['activities'] = activities
        return redirect(url_for('recommendations.recommendations'))
    return render_template('duration.html')

@main_bp.route('/trips')
@login_required
def trips():
    trips_data = fetch_trips_by_user(current_user.id)
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

    return render_template('trips.html', trips=trips_to_show)
