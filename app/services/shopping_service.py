import os
from serpapi import GoogleSearch
import json

def get_overall_outfit_image(query: str, gender: str = '') -> str:
    """Get one image representing the full outfit (from Google Images)"""
    api_key = os.getenv("SERPAPI_KEY")
    
    if not api_key:
        print("❌ SERPAPI_KEY not configured")
        return None
    
    full_query = f"{gender} {query}".strip()
    print(f"🖼️ [Images] Searching: {full_query}")

    params = {
        "engine": "google_images",
        "q": full_query,
        "google_domain": "google.com",
        "hl": "en",
        "gl": "us",
        "api_key": api_key
    }

    try:
        search = GoogleSearch(params)
        results = search.get_dict()

        print("🧾 RAW IMAGES RESPONSE:")
        print(json.dumps(results, indent=2)[:500])  # print first 500 characters only
        
        images = results.get("images_results", [])
        print(f"📸 Found {len(images)} images for '{full_query}'")

        if images:
            thumbnail = images[0].get("thumbnail")
            print("🔗 First Image URL:", thumbnail)
            return thumbnail

        return None
    except Exception as e:
        print(f"❌ Error getting outfit image: {e}")
        return None

def get_shopping_items(query: str, gender: str = '', num_results: int = 3) -> list[dict]:
    """Searches Google Shopping for product results, logs results for debugging."""
    api_key = os.getenv("SERPAPI_KEY")
    
    if not api_key:
        print("❌ SERPAPI_KEY not configured")
        return []
    
    full_query = f"{gender} {query}".strip()
    print(f"🛍️ [Shopping] Searching: {full_query}")

    params = {
        "engine": "google_shopping",
        "q": full_query,
        "google_domain": "google.com",
        "hl": "en",
        "gl": "us",
        "api_key": api_key
    }

    try:
        search = GoogleSearch(params)
        results = search.get_dict()

        products = results.get("shopping_results", [])[:num_results]
        print(f"🔎 Found {len(products)} products for '{full_query}'")

        for p in products:
            print("🧾", {
                "title": p.get("title"),
                "price": p.get("price"),
                "link": p.get("link"),
                "thumbnail": p.get("thumbnail"),
                "source": p.get("source")
            })

        return [
            {
                "title": p.get("title"),
                "price": p.get("price"),
                "link": p.get("link") or p.get("serpapi_product_api"),
                "thumbnail": p.get("thumbnail"),
                "source": p.get("source")
            }
            for p in products if p.get("title") and (p.get("link") or p.get("serpapi_product_api"))
        ]
    except Exception as e:
        print(f"❌ Error getting shopping items: {e}")
        return []
