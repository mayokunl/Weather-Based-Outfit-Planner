# app.py
import os
import markdown
import re
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash
from dotenv import load_dot
from openai_utils import get_recommendations, build_prompt_from_session
from weather_utils import get_weather_summary
from serp_utils import get_overall_outfit_image, get_shopping_items
from db import init_db
from db_utils import add_trip, add_user, fetch_trips_by_user

init_db()

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

@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        try:
            user = User.query.filter_by(email=form.email.data).first()
            password = form.password.data
            if user and check_password_hash(user.password, password):
                login_user(user)
                return redirect(url_for('workouts'))
            else:
                raise ValueError("Invalid Email/Password")
        except Exception as e:
            return render_template('login.html', form=form, message=e)
    return render_template('login.html', form=form)

@app.route("/signup", methods=["GET", "POST"])
def signup():
    form = RegistrationForm()
    if form.validate_on_submit():
        try:
            user_exists = User.query.filter_by(username=form.username.data).first()
            email_exists = User.query.filter_by(email=form.email.data).first()
            if user_exists:
                raise ValueError("User already exsists")
            if email_exists:
                raise ValueError("Email already in use")
            user = User(username=form.username.data, email=form.email.data, password=generate_password_hash(form.password.data))
            db.session.add(user)
            db.session.commit()
            flash(f'Account created for {form.username.data}!', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            message = f'An error has occured: {e}'
            return render_template("signup.html", form=form, message=message)
    return render_template("signup.html", form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        # save user with username, email, hashed password
        user = User(username=form.username.data, email=form.email.data, password=hash_pw(form.password.data))
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect(url_for('complete_profile'))  
    return render_template('register.html', form=form)

@app.route('/complete-profile', methods=['GET', 'POST'])
@login_required
def complete_profile():
    if request.method == 'POST':
        current_user.name = request.form['name']
        current_user.age = request.form['age']
        current_user.gender = request.form['gender']
        db.session.commit()
        return redirect(url_for('home'))  # or dashboard, etc.
    return render_template('complete_profile.html')


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

        # Go directly to recommendations
        return redirect(url_for('recommendations'))
    
    return render_template('duration.html')

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

    city = session.get('city')
    region = session.get('region')

    start_date = session.get('start_date')
    end_date = session.get('end_date')
    weather_summary = get_weather_summary(city, region, start_date, end_date)
    session['weather_summary'] = weather_summary
   
    gender = session.get("gender", "unisex").lower()

    prompt = build_prompt_from_session(session)
    response = get_recommendations(prompt)
    session['recommendations'] = response
    parsed_outfits = parse_daily_outfits(response)

    html_response = markdown.markdown(response)

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

    # 5) Render template with AI text, session data, and images dict
    return render_template(
        "recommendations.html",
        outfit_data=outfit_data,
        response=response,
        html_response=html_response,
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