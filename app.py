# app.py
import os
import markdown
import re
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session
from dotenv import load_dotenv
from openai_utils import get_recommendations, build_prompt_from_session

# Conditional imports for optional features
try:
    from weather_utils import get_weather_summary
except ImportError:
    def get_weather_summary(*args, **kwargs):
        return "Weather data unavailable"

try:
    from serp_utils import get_overall_outfit_image, get_shopping_items
except ImportError:
    def get_overall_outfit_image(*args, **kwargs):
        return None
    def get_shopping_items(*args, **kwargs):
        return []

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
        # Store form inputs into variables
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
        
        # Skip the separate activities page and go directly to recommendations
        return redirect(url_for('recommendations'))

def parse_daily_outfits(gpt_response):
    outfits = {}
    days = re.split(r'### Day (\d+):', gpt_response)

    # days = ['', '1', ' San Francisco\n**Outfit Recommendation:**\n- Top: ...', '2', ...]
    for i in range(1, len(days), 2):
        day_num = days[i].strip()
        content = days[i + 1]

        day_label = f"Day {day_num}"
        match = re.search(r'\*\*Search Query:\*\* (.*)', content)
        if match:
            query = match.group(1).strip()
            outfits[day_label] = query
        else:
            outfits[day_label] = "default outfit"

    return outfits

@app.route('/recommendations')
def recommendations():
    prompt = build_prompt_from_session(session)
    response = get_recommendations(prompt)
<<<<<<< HEAD
=======
    session['recommendations'] = response
    parsed_outfits = parse_daily_outfits(response)

    html_response = markdown.markdown(response)

    gender = session.get("gender", "unisex").lower()

    outfit_data = {}

    for day, outfit_query in parsed_outfits.items():
        print(f"🔍 FULL LOOK for: {outfit_query}")
        outfit_image = get_overall_outfit_image(outfit_query, gender)

        # Split outfit query into individual items
        item_keywords = [item.strip() for item in outfit_query.split(",")]
        shopping_links = []
        for item in item_keywords:
            products = get_shopping_items(item, gender)
            if products:
                shopping_links.append({"item": item, "results": products})

        outfit_data[day] = {
            "query": outfit_query,
            "image": outfit_image,
            "shopping": shopping_links
        }

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
>>>>>>> database_testing

    items = []
    for line in response.split('\n'):
        stripped = line.strip()
        if stripped.startswith('-'):
            items.append(stripped.lstrip('-').strip())

    # 4) Fetch 3 images per item via SerpAPI
    images = { item: get_image_urls(item, num_results=1) for item in items }

    # 5) Render template with AI text, session data, and images dict
    return render_template(
        "recommendations.html",
        outfit_data=outfit_data,
        response=response,
        data=session
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