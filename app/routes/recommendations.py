from flask import Blueprint, render_template, session, flash, redirect, url_for
import markdown
from flask_login import current_user, login_required
from app.services.weather_service import get_weather_summary
from app.services.genai_service import build_prompt_from_session, get_recommendations
from app.services.serp_service import get_overall_outfit_image, get_shopping_items
from app.services.database_service import add_trip_orm, DatabaseError, DatabaseValidationError
from app.services.session_service import TripPlanningSession
from app.utils.helpers import parse_daily_outfits
import logging

logger = logging.getLogger(__name__)

recommendations_bp = Blueprint('recommendations', __name__)

@recommendations_bp.route('/recommendations')
@login_required
def recommendations():
    try:
        # Get trip data from session service
        trip_data = TripPlanningSession.get_trip_data()
        
        # Validate required session data
        if not all([trip_data['city'], trip_data['region'], trip_data['start_date'], trip_data['end_date']]):
            flash('Missing trip information. Please start planning your trip again.', 'error')
            return redirect(url_for('main.destination'))
        
        weather_summary = get_weather_summary(trip_data['city'], trip_data['region'], trip_data['start_date'], trip_data['end_date'])
        TripPlanningSession.set_weather_summary(weather_summary)

        user_profile = TripPlanningSession.get_user_profile()
        prompt = build_prompt_from_session(session)
        response = get_recommendations(prompt)
        TripPlanningSession.set_recommendations(response)
        parsed_outfits = parse_daily_outfits(response)

        logger.info(f"AI Response preview: {response[:200]}...")
        logger.info(f"Parsed outfits: {parsed_outfits}")

        html_response = markdown.markdown(response)
        outfit_data = {}

        for day, outfit_query in parsed_outfits.items():
            logger.info(f"Processing {day} with query: {outfit_query}")
            
            outfit_image = get_overall_outfit_image(outfit_query, user_profile['gender'])
            logger.info(f"Got outfit image for {day}: {'Yes' if outfit_image else 'No'}")
            
            item_keywords = [item.strip() for item in outfit_query.split(",")]
            shopping_data = {}
            
            for item in item_keywords:
                logger.info(f"Searching for item: {item}")
                products = get_shopping_items(item, user_profile['gender'], num_results=3)
                logger.info(f"Found {len(products)} products for {item}")
                
                if products:
                    shopping_data[item] = {"products": products}
                    # Log first product for debugging
                    first_product = products[0]
                    logger.info(f"First product: {first_product.get('title', 'No title')[:50]}... - Link: {first_product.get('link', 'No link')[:50]}...")

            outfit_data[day] = {
                "query": outfit_query,
                "image": outfit_image,
                "shopping": shopping_data
            }

        # Save trip to database with error handling
        try:
            trip = add_trip_orm(
                user_id=current_user.id,
                city=trip_data['city'],
                region=trip_data['region'],
                gender=user_profile['gender'],
                age=user_profile['age'],
                activities=",".join(trip_data['activities']) if trip_data['activities'] else None,
                duration=trip_data['days'],
                weather=weather_summary,
                recommendations=response,
                outfit_data=outfit_data  # Save the complete outfit data
            )
            logger.info(f"Successfully saved trip with outfit data for user {current_user.id}")
        except (DatabaseError, DatabaseValidationError) as e:
            logger.error(f"Failed to save trip: {e}")
            flash('Trip recommendations generated, but failed to save to your history.', 'warning')
        except Exception as e:
            logger.error(f"Unexpected error saving trip: {e}")
            flash('Trip recommendations generated, but failed to save to your history.', 'warning')

        # Final logging
        logger.info(f"Final outfit_data keys: {list(outfit_data.keys())}")
        for day, data in outfit_data.items():
            logger.info(f"{day}: Image={'Yes' if data.get('image') else 'No'}, Shopping categories: {len(data.get('shopping', {}))}")

        return render_template("recommendations.html", outfit_data=outfit_data, response=response, html_response=html_response, data=session)
    
    except Exception as e:
        logger.error(f"Error generating recommendations: {e}")
        flash('An error occurred while generating recommendations. Please try again.', 'error')
        return redirect(url_for('main.destination'))
