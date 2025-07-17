# openai_utils.py

import os
from openai import OpenAI
from dotenv import load_dotenv
import logging

# Load environment variables from .env file
load_dotenv()

# Setup logging (optional but helpful for debugging)
logging.basicConfig(level=logging.INFO)

# Initialize OpenAI client with your API key
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# def build_prompt_from_session(session):
#     """
#     Constructs a natural-language prompt for the travel stylist based on session data.
#     """
#     activities = session.get('activities', [])
#     activities_text = ', '.join(activities) if activities else 'general travel'
#     weather_text = session.get('weather_summary', 'no weather data available')
#     days = session.get('days', 'multi-day')

#     prompt = f"""
# You are a travel stylist. Based on the following trip details:

# Location: {session.get('city', 'N/A')}, {session.get('region', 'N/A')}
# Gender: {session.get('gender', 'N/A')}
# Age: {session.get('age', 'N/A')}
# Activities: {activities_text}
# Duration: {days} days
# Weather Forecast: {weather_text}

# Your task:
# For each day of the trip, provide a detailed outfit recommendation that includes:
# - Complete outfit (top, bottom, shoes, accessories)
# - Adjustments based on weather conditions
# - Tailoring to the planned activities
# - Notes on whether each item should be packed or purchased

# Use a helpful and stylish tone.
# Format the response with clear Day-by-Day headings.
#     """
#     return prompt.strip()

HARD_CODED_GPT_RESPONSE = """
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

**Day 3: Leisurely Exploration**

Outfit Recommendation:
- Top: Flowy blouse or t-shirt
- Bottom: Denim shorts
- Shoes: Comfortable sneakers
- Accessories: Crossbody bag, sunglasses, and a delicate necklace
"""

def get_recommendations(prompt):
    """
    Sends the prompt to the OpenAI API and returns the generated outfit recommendations.
    """
    return HARD_CODED_GPT_RESPONSE  # For now, return the hardcoded response
    # try:
    #     logging.info("Sending prompt to OpenAI...")
    #     response = client.chat.completions.create(
    #         model="gpt-3.5-turbo",  # Use "gpt-4" or "gpt-4o" if desired
    #         messages=[
    #             {"role": "system", "content": "You are a helpful travel stylist."},
    #             {"role": "user", "content": prompt}
    #         ],
    #         max_tokens=1000,
    #         temperature=0.7
    #     )
    #     return response.choices[0].message.content
    # except Exception as e:
    #     logging.error(f"OpenAI API error: {e}")
    #     return f"Error getting recommendations: {str(e)}"