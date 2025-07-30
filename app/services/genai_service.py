
import os
from openai import OpenAI
from dotenv import load_dotenv
import logging
import re

# Load environment variables from .env file
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)

# Initialize OpenAI client with your API key
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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
    
    **Day [Number] ([Date]): [Specific Activity] in [Weather Summary]**
    
    **Weather Adjustments:** [Specific weather-based adjustments like sunscreen, layers, etc.]
    
    **Complete Outfit:**
    - Top: [specific item with details]
    - Bottom: [specific item with details]  
    - Shoes: [specific item with details]
    - Accessories: [specific items with details]
    
    **Activity Considerations:** [How the outfit works for the planned activities]
    **Packing Notes:** [Whether items should be packed or purchased]
    
    **Product Searches:**
    - Top: [specific brand/style/color top query]
    - Bottom: [specific brand/style/color bottom query]  
    - Shoes: [specific brand/style/color shoes query]
    - Accessories: [specific accessory queries]
    
    Make the search queries specific with:
    - Brand suggestions when relevant
    - Specific styles/cuts (e.g. "slim fit", "relaxed", "high-waisted")
    - Colors that work for the weather/activities
    - Material types (e.g. "cotton", "merino wool", "waterproof")
    
    IMPORTANT: The outfit recommendations should be specifically tailored to the actual activities and city listed above. DO NOT use the example values below. Use only the city, activity, and weather from the trip details above.
    
    Example format (do NOT copy the values, only the structure!):
    **Day 1 ([Date]): [Activity] in [City] [Weather Summary]**
    
    **Weather Adjustments:** [Weather-based adjustments]
    
    **Complete Outfit:**
    - Top: [item]
    - Bottom: [item]
    - Shoes: [item]
    - Accessories: [items]
    
    **Activity Considerations:** [How the outfit works for the planned activities]
    **Packing Notes:** [Whether items should be packed or purchased]
    
    **Product Searches:**
    - Top: [query]
    - Bottom: [query]
    - Shoes: [query]
    - Accessories: [query]
    
    Use a helpful and stylish tone.
    Format each day with the exact format shown above, but adapt the content to match the actual activities and city from the trip details.
    """
    return prompt.strip()

def parse_daily_outfits_with_products(gpt_response):
    """
    Parse the AI response to extract both outfit descriptions and specific product search queries
    """
    outfits = {}
    
    # Split by days
    days = re.split(r'### Day (\d+):', gpt_response)
    
    for i in range(1, len(days), 2):
        day_num = days[i].strip()
        content = days[i + 1]
        day_label = f"Day {day_num}"
        
        # Extract product searches section
        product_section = re.search(r'\*\*Product Searches:\*\*(.*?)(?=\n###|\n\*\*|$)', content, re.DOTALL)
        
        if product_section:
            product_text = product_section.group(1).strip()
            
            # Parse individual product lines
            product_queries = {}
            for line in product_text.split('\n'):
                line = line.strip()
                if line.startswith('- '):
                    # Remove the "- " prefix
                    line = line[2:]
                    if ':' in line:
                        category, query = line.split(':', 1)
                        product_queries[category.strip()] = query.strip()
            
            outfits[day_label] = {
                'content': content,
                'products': product_queries
            }
        else:
            # Fallback to old method if new format not found
            match = re.search(r'\*\*Search Query:\*\* (.*)', content)
            general_query = match.group(1).strip() if match else "default outfit"
            outfits[day_label] = {
                'content': content,
                'products': {'general': general_query}
            }
    
    return outfits

def get_recommendations(prompt):
    """
    Sends the prompt to the OpenAI API and returns the generated outfit recommendations.
    """
    try:
        logging.info("Sending enhanced prompt to OpenAI...")
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful travel stylist that provides detailed outfit recommendations."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2000,
            temperature=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        logging.error(f"OpenAI API error: {e}")
        return f"Error getting recommendations: {str(e)}"

# Enhanced SERP API integration
def get_product_with_real_links(query: str, gender: str = '', num_results: int = 5) -> list[dict]:
    """
    Enhanced version that gets more specific product results with better filtering
    """
    from serp_service import get_shopping_items
    
    # Add gender and make query more specific for shopping
    enhanced_query = f"{gender} {query} buy online shop".strip()
    
    products = get_shopping_items(enhanced_query, gender, num_results)
    
    # Filter out products without proper links
    valid_products = []
    for product in products:
        if (product.get('link') and 
            product.get('title') and 
            product.get('price') and
            not product['link'].startswith('javascript:') and
            'http' in product['link']):
            valid_products.append(product)
    
    return valid_products

def get_outfit_inspiration_image(day_outfit_content: str, gender: str = '') -> str:
    """
    Generate a search query for overall outfit inspiration based on the day's content
    """
    from serp_utils import get_overall_outfit_image
    
    # Extract key clothing items from the content
    clothing_keywords = []
    
    # Look for common clothing terms in the content
    clothing_items = [
        'tank top', 'shirt', 'blouse', 'sweater', 'jacket', 'coat',
        'jeans', 'pants', 'shorts', 'skirt', 'dress', 'leggings',
        'sneakers', 'boots', 'sandals', 'heels', 'flats',
        'hat', 'sunglasses', 'scarf', 'bag', 'backpack'
    ]
    
    content_lower = day_outfit_content.lower()
    for item in clothing_items:
        if item in content_lower:
            clothing_keywords.append(item)
    
    # Create a search query from found items (max 4 items)
    if clothing_keywords:
        outfit_query = ' '.join(clothing_keywords[:4])
    else:
        outfit_query = "casual travel outfit"
    
    return get_overall_outfit_image(outfit_query, gender)