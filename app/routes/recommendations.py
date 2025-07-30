from urllib import response
from flask import Blueprint, render_template, session, flash, redirect, url_for
import os, json
import markdown
from flask_login import current_user, login_required
from app.services.weather_service import get_weather_summary
from app.services.genai_service import build_prompt_from_session, get_recommendations
from app.services.serp_service import get_overall_outfit_image, get_shopping_items
from app.services.database_service import add_trip_orm, DatabaseError, DatabaseValidationError
from app.services.session_service import TripPlanningSession
from app.utils.helpers import parse_daily_outfits, remove_product_searches_section
import re
import logging

logger = logging.getLogger(__name__)

recommendations_bp = Blueprint('recommendations', __name__)

@recommendations_bp.route('/recommendations')
@login_required
def recommendations():
    try:
        print("=== RECOMMENDATIONS ROUTE DEBUG ===")
        print(f"Session data: {dict(session)}")
        # === FORCE LOAD FROM CACHE FOR USER 5 (DEV ONLY) ===
        cache_dir = os.path.join(os.path.dirname(__file__), '../../instance')
        os.makedirs(cache_dir, exist_ok=True)
        cache_file = os.path.join(cache_dir, f'recommendations_cache_5.json')
        if os.path.exists(cache_file):
            print(f"🧾 Reading cache file from: {cache_file}")
            with open(cache_file, 'r') as f:
                cache = json.load(f)
            print(f"📦 Loaded cache content keys: {list(cache.keys())}")
            print("📄 Cache data preview:")
            print(json.dumps(cache, indent=2)[:1000])
            print('Loaded recommendations from cache (dev override).')
            # Only remove keys related to trip data, keep login/session keys
            preserved_keys = {'_user_id', '_fresh', '_id', '_flashes', 'csrf_token'}
            keys_to_remove = [k for k in session.keys() if k not in preserved_keys]
            for key in keys_to_remove:
                session.pop(key)
            # Overwrite session with trip data from cache for dev
            for k, v in cache['data'].items():
                session[k] = v
            return render_template(
                'recommendations.html',
                data=cache['data'],
                response=cache['response'],
                days=cache['days'],
                outfit_data=cache['outfit_data']
            )
        # ---
        # The following code is commented out during dev cache override to avoid undefined variable errors.
        # ---
        # Check if all required data is present
        # required_fields = ['city', 'start_date', 'end_date', 'days', 'activities']
        # missing_fields = [field for field in required_fields if not trip_data.get(field)]
        # if missing_fields:
        #     flash(f'Missing information: {", ".join(missing_fields)}. Please complete your trip planning.', 'error')
        #     return redirect(url_for('main.destination'))
        # print("All required session data present, proceeding with recommendations...")
        # try:
        #     weather_summary = get_weather_summary(
        #         trip_data['city'],
        #         trip_data['region'],
        #         trip_data['start_date'],
        #         trip_data['end_date']
        #     )
        # except Exception as weather_exc:
        #     logger.error(f"Error fetching weather summary: {weather_exc}")
        #     weather_summary = 'Weather data not available'
        # template_data = {
        #     'city': trip_data['city'],
        #     'region': trip_data['region'],
        #     'start_date': trip_data['start_date'],
        #     'end_date': trip_data['end_date'],
        #     'days': trip_data['days'],
        #     'activities': trip_data['activities'],
        #     'weather_summary': weather_summary,
        #     'gender': user_profile.get('gender', 'unisex'),
        #     'age': user_profile.get('age', 'N/A')
        # }
        # trip_data_with_weather = dict(trip_data)
        # trip_data_with_weather['weather_summary'] = weather_summary
        # prompt = build_prompt_from_session(trip_data_with_weather)
        # response = get_recommendations(prompt)
        # print(f"Raw OpenAI response: {response[:200] if response else 'No response'}...")
        # days = parse_daily_outfits(response, template_data['gender'])
        # for day in days:
        #     day['content'] = remove_product_searches_section(day['content'])
        # outfit_data = {}
        # for day in days:
        #     day_title = day.get('title', 'Day')
        #     content = day.get('content', '')
        #     gender = template_data.get('gender', '')
        #     complete_outfit_match = re.search(r'\*\*Complete Outfit:\*\*(.*?)(\*\*|$)', content, re.DOTALL)
        #     shopping_items = []
        #     if complete_outfit_match:
        #         outfit_section = complete_outfit_match.group(1)
        #         item_lines = re.findall(r'-\s*([A-Za-z ]+):\s*(.+)', outfit_section)
        #         for item_type, item_desc in item_lines:
        #             item_query = f"{gender} {item_desc}".strip()
        #             logger.info(f"Searching for: {item_query}")
        #             results = get_shopping_items(item_desc, gender, num_results=1)
        #             if results:
        #                 shopping_items.append(results[0])
        #             else:
        #                 shopping_items.append({
        #                     'title': item_desc,
        #                     'source': None,
        #                     'price': None,
        #                     'thumbnail': None,
        #                     'link': None
        #                 })
        #     else:
        #         logger.warning(f"No 'Complete Outfit' section found for {day_title}")
        #     outfit_data[day_title] = {
        #         'content': content,
        #         'shopping': shopping_items
        #     }
        # print(f"Built outfit_data with shopping items: {list(outfit_data.keys())}")
        # activities_str = ','.join(trip_data['activities']) if isinstance(trip_data['activities'], list) else (trip_data['activities'] or '')
        # try:
        #     add_trip_orm(
        #         user_id=current_user.id,
        #         city=trip_data['city'],
        #         region=trip_data['region'] or '',
        #         gender=template_data['gender'],
        #         age=template_data['age'],
        #         activities=activities_str,
        #         duration=trip_data['days'],
        #         weather=weather_summary,
        #         recommendations=response,
        #         outfit_data={'days': days, 'outfit_data': outfit_data}
        #     )
        # except DatabaseValidationError as db_val_exc:
        #     logger.error(f"Validation error saving trip: {db_val_exc}")
        #     flash(f'Could not save trip: {db_val_exc}', 'warning')
        # except DatabaseError as db_exc:
        #     logger.error(f"Error saving trip to database: {db_exc}")
        #     flash('Could not save trip to your profile. Please try again later.', 'warning')
        # with open(cache_file, 'w') as f:
        #     json.dump({
        #         'data': template_data,
        #         'response': response,
        #         'days': days,
        #         'outfit_data': outfit_data
        #     }, f)
        # print('Saved recommendations to cache.')
        # return render_template(
        #     'recommendations.html',
        #     data=template_data,
        #     response=response,
        #     days=days,
        #     outfit_data=outfit_data
        # )
    
    except Exception as e:
        logger.error(f"Error generating recommendations: {e}")
        print(f"ERROR in recommendations route: {e}")
        flash('An error occurred while generating recommendations. Please try again.', 'error')
        return redirect(url_for('main.destination'))
