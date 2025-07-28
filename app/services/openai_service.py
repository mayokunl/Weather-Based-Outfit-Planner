import os
from openai import OpenAI
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)

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
    At the end of each day's section, include a one-line Google image search query summarizing the core outfit (only clothes/accessories). Keep it short and specific.

    Label it like:  
    **Search Query:** tank top, leggings, hiking boots

    Use a helpful and stylish tone.
    Format the response with clear Day-by-Day headings.
        """
    return prompt.strip()

def get_recommendations(prompt):
    """
    Sends the prompt to the OpenAI API and returns the generated outfit recommendations.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        return "OpenAI API key not configured."
    
    client = OpenAI(api_key=api_key)
    
    try:
        logging.info("Sending prompt to OpenAI...")
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful travel stylist."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        logging.error(f"OpenAI API error: {e}")
        return f"Error getting recommendations: {str(e)}"
