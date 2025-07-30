#!/usr/bin/env python3
"""Test SerpAPI functionality"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from app.services.shopping_service import get_shopping_items, get_overall_outfit_image

def test_serpapi():
    print("🧪 Testing SerpAPI Integration...")
    
    # Test API key
    api_key = os.getenv("SERPAPI_KEY")
    print(f"🔑 API Key configured: {'✓' if api_key else '✗'}")
    
    if api_key:
        print(f"🔑 API Key preview: {api_key[:10]}...{api_key[-10:]}")
    
    # Test shopping search
    print("\n🛍️ Testing shopping search...")
    products = get_shopping_items("summer dress", "women", num_results=2)
    print(f"📦 Found {len(products)} products")
    
    for i, product in enumerate(products, 1):
        print(f"  {i}. {product.get('title', 'No title')[:50]}...")
        print(f"     Price: {product.get('price', 'No price')}")
        print(f"     Link: {product.get('link', 'No link')}")
    
    # Test image search  
    print("\n🖼️ Testing image search...")
    image_url = get_overall_outfit_image("summer dress", "women")
    print(f"🖼️ Image URL: {image_url}")
    
if __name__ == "__main__":
    test_serpapi()
