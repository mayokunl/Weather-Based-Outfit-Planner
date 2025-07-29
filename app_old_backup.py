import os
import markdown
import requests
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_migrate import Migrate
from dotenv import load_dotenv
from genai_utils import get_recommendations, build_prompt_from_session
from weather_utils import get_weather_summary
from serp_utils import get_overall_outfit_image, get_shopping_items
from db import init_db
from db_utils import add_trip, add_user, fetch_trips_by_user
from forms import RegistrationForm, LoginForm
from werkzeug.security import generate_password_hash, check_password_hash

# Initialize app
init_db()
load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'dev')

# DB setup
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Models
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"



with app.app_context():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# Enhanced parsing functions
def parse_daily_outfits_with_products(gpt_response):
    """
    Parse the AI response to extract both outfit descriptions and specific product search queries
    Updated to handle the current AI response format
    """
    outfits = {}
    
    # Split by days - handle both "Day 1:" and "Day 1: Title" formats
    days = re.split(r'Day (\d+):', gpt_response)
    
    for i in range(1, len(days), 2):
        day_num = days[i].strip()
        content = days[i + 1]
        day_label = f"Day {day_num}"
        
        # Look for "Product Searches:" section (note the colon)
        product_section = re.search(r'Product Searches:(.*?)(?=Day \d+:|$)', content, re.DOTALL)
        
        if product_section:
            product_text = product_section.group(1).strip()
            print(f"🔍 Found product section for {day_label}: {product_text[:100]}...")
            
            # Parse the product lines - handle the current format
            product_queries = {}
            lines = product_text.split('\n')
            
            for line in lines:
                line = line.strip()
                if line.startswith('- '):
                    # Remove the "- " prefix
                    line = line[2:].strip()
                    
                    # Handle format like: Top: "query1" or "query2" or "query3"
                    if ':' in line:
                        category_part, queries_part = line.split(':', 1)
                        category = category_part.strip()
                        
                        # Extract the first quoted query (or the whole thing if no quotes)
                        queries_part = queries_part.strip()
                        
                        # Try to find first quoted string
                        quote_match = re.search(r'"([^"]+)"', queries_part)
                        if quote_match:
                            query = quote_match.group(1)
                        else:
                            # Take everything up to " or " if present
                            query = queries_part.split(' or ')[0].strip().strip('"')
                        
                        product_queries[category] = query
                        print(f"  📝 {category}: {query}")
            
            outfits[day_label] = {
                'content': content,
                'products': product_queries
            }
        else:
            print(f"❌ No product section found for {day_label}")
            # Fallback - create some basic queries from the content
            fallback_queries = extract_fallback_queries(content)
            outfits[day_label] = {
                'content': content,
                'products': fallback_queries
            }
    
    return outfits

def extract_fallback_queries(content):
    """Extract basic clothing items from content if structured parsing fails"""
    queries = {}
    content_lower = content.lower()
    
    # Basic clothing detection
    if 'rash guard' in content_lower or 'tank top' in content_lower or 'shirt' in content_lower:
        queries['Top'] = 'quick dry shirt swimwear'
    
    if 'swim trunks' in content_lower or 'bikini' in content_lower or 'shorts' in content_lower:
        queries['Bottom'] = 'swim shorts beach wear'
    
    if 'flip-flops' in content_lower or 'water shoes' in content_lower or 'sandals' in content_lower:
        queries['Shoes'] = 'beach sandals water shoes'
    
    if 'hat' in content_lower or 'sunglasses' in content_lower:
        queries['Accessories'] = 'sun hat beach accessories'
    
    return queries

# Routes
@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        try:
            user = User.query.filter_by(email=form.email.data).first()
            if user and check_password_hash(user.password, form.password.data):
                login_user(user)
                session['user_id'] = user.id
                return redirect(url_for('home'))
            else:
                raise ValueError("Invalid Email/Password")
        except Exception as e:
            return render_template('login.html', form=form, message=e)
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user_exists = User.query.filter_by(username=form.username.data).first()
        email_exists = User.query.filter_by(email=form.email.data).first()
        if user_exists or email_exists:
            flash('User or email already exists.', 'error')
            return render_template('register.html', form=form)
        hashed_pw = generate_password_hash(form.password.data)
        user = User(username=form.username.data, email=form.email.data, password=hashed_pw)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        session['user_id'] = user.id
        return redirect(url_for('complete_profile'))
    return render_template('register.html', form=form)




@app.route('/completeProfile', methods=['GET', 'POST'])
@login_required
def complete_profile():
    if request.method == 'POST':
        current_user.name = request.form['name']
        current_user.age = request.form['age']
        current_user.gender = request.form['gender']
        db.session.commit()
        session['age'] = current_user.age
        session['gender'] = current_user.gender
        return redirect(url_for('home'))
    return render_template('completeProfile.html')

@app.route('/destination', methods=['GET', 'POST'])
@login_required
def destination():
    if request.method == 'POST':
        session['city'] = request.form.get('city', '')
        session['region'] = request.form.get('region', '')
        return redirect(url_for('duration'))
    return render_template('destination.html')

@app.route('/duration', methods=['GET', 'POST'])
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
        return redirect(url_for('recommendations'))
    return render_template('duration.html')

@app.route('/recommendations')
def recommendations():
    city = session.get('city')
    region = session.get('region')
    start_date = session.get('start_date')
    end_date = session.get('end_date')
    
    # Get weather summary
    weather_summary = get_weather_summary(city, region, start_date, end_date)
    session['weather_summary'] = weather_summary
    
    gender = session.get("gender", "unisex").lower()
    
    # Build enhanced prompt and get AI recommendations
    prompt = build_prompt_from_session(session)
    response = get_recommendations(prompt)
    session['recommendations'] = response
    
    print("🤖 AI Response preview:", response[:200])
    
    # Parse the enhanced response with product searches
    parsed_outfits = parse_daily_outfits_with_products(response)
    
    # Convert markdown for display
    html_response = markdown.markdown(response)
    
    # Process each day's outfit
    outfit_data = {}
    for day, day_data in parsed_outfits.items():
        print(f"\n🗓️ Processing {day}")
        day_content = day_data['content']
        product_queries = day_data['products']
        
        print(f"📝 Product queries found: {list(product_queries.keys())}")
        
        # Get overall outfit inspiration image - create a general query from all products
        general_query = " ".join(product_queries.values())[:50]  # Limit length
        print(f"🖼️ Getting inspiration image for: {general_query}")
        outfit_image = get_overall_outfit_image(general_query, gender)
        
        # Get specific products for each category with REAL LINKS
        shopping_results = {}
        for category, query in product_queries.items():
            print(f"\n🛍️ Searching {category}: {query}")
            
            # Use the enhanced function that gets real product links
            products = get_shopping_items(query, gender, num_results=3)
            
            if products:
                shopping_results[category] = {
                    'query': query,
                    'products': products
                }
                print(f"✅ Found {len(products)} products for {category}")
                
                # Print first product details for debugging
                if products:
                    first_product = products[0]
                    print(f"   🔗 First product: {first_product.get('title', 'No title')[:30]}...")
                    print(f"   💰 Price: {first_product.get('price', 'No price')}")
                    print(f"   🏪 Store: {first_product.get('source', 'No source')}")
                    print(f"   🌐 Primary Link: {first_product.get('link', 'No link')}")
                    
                    # Show purchase options if available
                    if first_product.get('purchase_options'):
                        print(f"   🛒 Purchase options: {len(first_product['purchase_options'])}")
                        for i, option in enumerate(first_product['purchase_options'][:2]):
                            print(f"      {i+1}. {option['source']}: {option['price']} - {option['link'][:50]}...")
            else:
                print(f"❌ No products found for {category}: {query}")
        
        outfit_data[day] = {
            'content': day_content,
            'image': outfit_image,
            'shopping': shopping_results,
            'all_queries': product_queries  # Keep all queries for debugging
        }
        
        print(f"✅ {day} processed - Image: {'✓' if outfit_image else '✗'}, Categories: {len(shopping_results)}")
    
    # Save trip to database
    add_trip(
        user_id=session['user_id'],
        city=city,
        region=region,
        gender=gender,
        age=session.get('age'),
        activities=",".join(session.get('activities', [])) if session.get('activities') else None,
        duration=session.get('days'),
        weather=weather_summary,
        recommendations=response
    )
    
    print(f"\n🎯 Final outfit_data keys: {list(outfit_data.keys())}")
    for day, data in outfit_data.items():
        print(f"   {day}: {len(data['shopping'])} categories, image: {'✓' if data['image'] else '✗'}")
        # Show links status for each category
        for category, category_data in data['shopping'].items():
            products_with_links = sum(1 for p in category_data['products'] if p.get('link'))
            print(f"      {category}: {products_with_links}/{len(category_data['products'])} products have links")
    
    return render_template(
        "recommendations.html", 
        outfit_data=outfit_data, 
        response=response, 
        html_response=html_response, 
        data=session
    )

@app.route('/closet/add', methods=['POST'])
@login_required
def add_to_closet():
    title = request.form.get('title')
    price = request.form.get('price')
    image_url = request.form.get('image')

    if title and image_url:
        item = ClosetItem(
            user_id=current_user.id,
            title=title,
            price=price,
            image_url=image_url
        )
        db.session.add(item)
        db.session.commit()
        flash("Item added to your closet!", "success")

    return redirect(request.referrer or url_for('home'))

@app.route('/closet/view')
@login_required
def view_closet():
    items = ClosetItem.query.filter_by(user_id=current_user.id).all()
    return render_template('closet.html', items=items)

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

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True, port=5001)