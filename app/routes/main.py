from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from flask_login import login_required, current_user

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
        
        # Store in session for now
        session['city'] = city
        session['region'] = region
        
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

@main_bp.route('/trips')
@login_required
def trips():
    # For now, just return a simple trips page
    return render_template('trips.html')