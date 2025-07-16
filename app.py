# app.py
from flask import Flask, render_template, request, redirect, url_for, session
from dotenv import load_dotenv
from openai_utils import build_prompt_from_session, get_recommendations
from db_utils import add_user
import os
import db
import db_utils

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
        session['email']  = request.form.get('email', '')
        user_id = add_user(username, email)
        session['age']    = request.form.get('age', '')
        session['gender'] = request.form.get('gender', '')
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
        # Handle both duration and activities from the combined form
        session['days'] = request.form.get('days', '')
        
        # Get all activities from the form (multiple inputs with same name)
        activities = request.form.getlist('activities')
        session['activities'] = activities
        
        # Skip the separate activities page and go directly to recommendations
        return redirect(url_for('recommendations'))
    return render_template('duration.html')

@app.route('/recommendations')
def recommendations():
    # Generate AI recommendations using session data
    prompt = build_prompt_from_session(session)
    response = get_recommendations(prompt)
    
    # Pass both the AI response and session data to the template
    return render_template('recommendations.html', response=response, data=session)
    


if __name__ == '__main__':
    app.run(debug=True, port=5001)
