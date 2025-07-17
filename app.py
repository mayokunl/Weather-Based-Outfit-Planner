# app.py
import os
from flask import Flask, render_template, request, redirect, url_for, session
from dotenv import load_dotenv
from openai_utils import build_prompt_from_session, get_recommendations
from weather_utils import get_weather_summary
from serp_utils import get_image_urls

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
        # store basic profile info in session
        session['name']   = request.form.get('name', '')
        session['age']    = request.form.get('age', '')
        session['gender'] = request.form.get('gender', '')
        session['email']  = request.form.get('email', '')
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

from serp_utils import get_image_urls

@app.route('/recommendations')
def recommendations():
    # Pull data from session
    gender = session.get('gender', 'unisex').lower()
    age = int(session.get('age', 25))
    activities = session.get('activities', [])

    # --- OpenAI GPT: Generate outfit text recommendations ---
    prompt = build_prompt_from_session(session)
    response = get_recommendations(prompt)

    # --- SerpAPI: Fetch 1 outfit image per activity ---
    image_results = []
    for activity in activities:
        query = f"{gender} {activity} outfit"
        urls = get_image_urls(query, num_results=1)
        if urls:
            image_results.append({
                "activity": activity,
                "image_url": urls[0],
                "query": query
            })

    # Convert to dict format for the template: {activity: [image_url]}
    images_by_activity = {item['activity']: [item['image_url']] for item in image_results}

    # --- Pass all data to template ---
    return render_template(
        "recommendations.html",
        data=session,
        response=response,
        images=images_by_activity
    )

if __name__ == '__main__':
    app.run(debug=True, port=5001)