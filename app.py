# app.py
import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from dotenv import load_dotenv
from openai_utils import build_prompt_from_session, get_recommendations
from weather_utils import get_weather_summary
from serp_utils import get_image_urls
from db import init_db
init_db()
from db_utils import add_trip, add_user, fetch_trips_by_user
from datetime import datetime


# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'dev')   # Use env variable or fallback to 'dev'

@app.route('/')
def index():
    return redirect(url_for('register'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    print("== Rendering register route ==")
    if request.method == 'POST':
        # Get form inputs into variables
        name = request.form.get('name', '')
        age = request.form.get('age', '')
        gender = request.form.get('gender', '')
        email = request.form.get('email', '')

        # Store in session
        session['name'] = name
        session['age'] = age
        session['gender'] = gender
        session['email'] = email

        # Save user to DB and store user_id in session
        user_id = add_user(username=name, email=email)  # assuming add_user takes these args
        session['user_id'] = user_id

        return redirect(url_for('destination'))
    return render_template('register.html')

@app.route('/destination', methods=['GET', 'POST'])
def destination():
    if request.method == 'POST':
        session['city']   = request.form.get('city', '')
        session['region'] = request.form.get('region', '')
        return redirect(url_for('duration'))
    return render_template('destination.html')

@app.route('/duration', methods=['GET', 'POST'])
def duration():
     if request.method == 'POST':
        # Trip dates
        start_date = request.form.get('start_date')
        end_date   = request.form.get('end_date')
        session['start_date'] = start_date
        session['end_date']   = end_date

        # Compute number of days
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d')
            end   = datetime.strptime(end_date, '%Y-%m-%d')
            days = (end - start).days + 1
        except Exception:
            days = None
        session['days'] = days

        # Get activities
        activities = request.form.getlist('activities')
        session['activities'] = activities

        return redirect(url_for('recommendations'))
     return render_template('duration.html')

@app.route('/recommendations')
def recommendations():
    # Fetch weather summary and store in session
    city       = session.get('city')
    region     = session.get('region')
    start_date = session.get('start_date')
    end_date   = session.get('end_date')
    if city and region and start_date and end_date:
        weather_summary = get_weather_summary(city, region, start_date, end_date)
    else:
        weather_summary = "Weather data unavailable."
    session['weather_summary'] = weather_summary

    # Generate AI recommendations using session data
    prompt = build_prompt_from_session(session)
    response = get_recommendations(prompt)
    session['recommendations'] = response

    # Save trip to database here
    add_trip(
        user_id=session['user_id'],
        city=city,
        region=region,
        gender=session.get('gender'),
        age=session.get('age'),
        activities=",".join(session.get('activities', [])) if session.get('activities') else None,
        duration=session.get('days'),
        weather=weather_summary,
        recommendations=response
    )

    items = []
    for line in response.split('\n'):
        stripped = line.strip()
        if stripped.startswith('-'):
            items.append(stripped.lstrip('-').strip())

    # 4) Fetch 3 images per item via SerpAPI
    images = { item: get_image_urls(item, num_results=1) for item in items }

    # 5) Render template with AI text, session data, and images dict
    return render_template(
        'recommendations.html',
        response=response,
        data=session,
        images=images
    )


@app.route('/trips')
def trips():
    user_id = session.get('user_id')
    if not user_id:
        flash("Please log in to view your trips.", "error")
        return redirect(url_for('login'))

    trips_data = fetch_trips_by_user(user_id)

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


if __name__ == '__main__':
    app.run(debug=True, port=5001)