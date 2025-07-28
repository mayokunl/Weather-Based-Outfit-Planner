from flask import Blueprint, render_template, session
import markdown
from app.services.weather_service import get_weather_summary
from app.services.openai_service import build_prompt_from_session, get_recommendations
from app.services.shopping_service import get_overall_outfit_image, get_shopping_items
from app.utils.helpers import parse_daily_outfits
from app.database.db_utils import add_trip

recommendations_bp = Blueprint('recommendations', __name__)

@recommendations_bp.route('/recommendations')
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
        outfit_image = get_overall_outfit_image(outfit_query, gender)
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

    return render_template("recommendations.html", outfit_data=outfit_data, response=response, html_response=html_response, data=session)
