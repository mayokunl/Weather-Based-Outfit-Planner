# openai_utils.py (using Gemini)
import os
import google.generativeai as genai
from dotenv import load_dotenv
import logging

# Load environment variables from .env file
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)

# Initialize Gemini client with your API key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel(model_name="gemini-1.5-flash")

def build_prompt_from_session(session):
    """
    Constructs a natural-language prompt for the travel stylist based on session data.
    """
    activities = session.get('activities', [])
    activities_text = ', '.join(activities) if activities else 'general travel'
    weather_text = session.get('weather_summary', 'no weather data available')
    days = session.get('days', 'multi-day')

    prompt = f"""
    You are a travel stylist. Based on the following trip details:

    Location: {session.get('city', 'N/A')}, {session.get('region', 'N/A')}
    Gender: {session.get('gender', 'N/A')}
    Age: {session.get('age', 'N/A')}
    Activities: {activities_text}
    Duration: {days} days
    Weather Forecast: {weather_text}

    Your task:
    For each day of the trip, provide a detailed outfit recommendation that includes:
    - Complete outfit (top, bottom, shoes, accessories)
    - Adjustments based on weather conditions
    - Tailoring to the planned activities
    - Notes on whether each item should be packed or purchased
    At the end of each day’s section, include a one-line Google image search query summarizing the core outfit (only clothes/accessories). Keep it short and specific.

    Label it like:  
    **Search Query:** tank top, leggings, hiking boots

    Use a helpful and stylish tone.
    Format the response with clear Day-by-Day headings.
    """
    return prompt.strip()

HARD_CODED_GPT_RESPONSE = """
### Day 1: San Francisco
**Outfit Recommendation:**
- Top: Lightweight breathable tank top
- Bottom: Comfy athletic shorts
- Shoes: Sturdy hiking sandals
- Accessories: Wide-brimmed hat, sunglasses, small backpack
- Adjustments: Layer with a light jacket for the cooler evenings
- Tailoring: Opt for moisture-wicking fabrics for hiking comfort
- Packing/Purchase: Pack the accessories, purchase if needed
**Search Query:** tank top, athletic shorts, hiking sandals
"""

def get_recommendations(prompt):
    """
    Sends the prompt to the Gemini API and returns the generated outfit recommendations.
    """
    try:
        logging.info("Sending prompt to Gemini...")
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        logging.error(f"Gemini API error: {e}")
        return f"Error getting recommendations: {str(e)}"