# openai_utils.py

from openai import OpenAI
import os
from dotenv import load_dotenv

#hardcoded response
HARDCODED_RESPONSE = """
**Day 1: Hiking Adventure**

Outfit Recommendation:
- Top: Moisture-wicking tank top
- Bottom: Comfortable and breathable leggings
- Shoes: Sturdy hiking boots
- Accessories: Wide-brim hat, sunglasses, and a small backpack

**Day 2: Swimming Fun**

Outfit Recommendation:
- Top: Bright-colored bikini top
- Bottom: Matching bikini bottoms
- Shoes: Flip-flops
- Accessories: Sun hat, beach towel, and waterproof phone case
"""

# Load environment variables from .env file
load_dotenv()

# Initialize OpenAI client
# client = OpenAI(api_key=os.getenv('OPENAI_API_KEY')) #COMMENTED OUT

def build_prompt_from_session(session):
    # Handle activities list (from the new combined form)
    activities = session.get('activities', [])
    activities_text = ', '.join(activities) if activities else 'general travel'
    
    weather_text = session.get('weather_summary', 'no weather data available')
    return f"""
        You are a travel stylist. Based on the following trip details:

        Location: {session.get('city', 'N/A')}, {session.get('region', 'N/A')}
        Gender:   {session.get('gender', 'N/A')}
        Age:      {session.get('age', 'N/A')}
        Activities: {', '.join(session.get('activities', [])) or 'general travel'}
        Duration:   {session.get('days', 'N/A')} days

        Here is the weather forecast for each day of the trip:
        {weather_text}

    Please provide specific outfit recommendations for this {session.get('days', 'multi-day')} day trip. For each day, suggest:
    - Complete outfit (top, bottom, shoes, accessories)
    - Weather-appropriate clothing
    - Activity-specific recommendations
    - Packing vs. shopping suggestions
    - Use a helpful and stylish tone

    Format your response with clear day-by-day recommendations.
    """

def get_recommendations(prompt):
    try:
        # Use hardcoded response for now
        return HARDCODED_RESPONSE

        return response.choices[0].message.content
    except Exception as e:
        return f"Error getting recommendations: {str(e)}"