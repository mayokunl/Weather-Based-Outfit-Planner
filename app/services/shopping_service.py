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

        processed_products = []
        for p in products:
            # Get the link - prefer direct links, fallback to SerpAPI
            product_link = p.get("link")
            
            # If no direct link, try to construct a search URL for the store
            if not product_link or 'serpapi.com' in product_link:
                store_name = p.get("source", "").lower()
                product_title = p.get("title", "")
                
                # Create a search URL for popular stores
                if "amazon" in store_name:
                    search_query = product_title.replace(" ", "+")
                    product_link = f"https://www.amazon.com/s?k={search_query}"
                elif "target" in store_name:
                    search_query = product_title.replace(" ", "%20")
                    product_link = f"https://www.target.com/s?searchTerm={search_query}"
                elif "walmart" in store_name:
                    search_query = product_title.replace(" ", "%20")
                    product_link = f"https://www.walmart.com/search?q={search_query}"
                elif "loft" in store_name:
                    search_query = product_title.replace(" ", "%20")
                    product_link = f"https://www.loft.com/search?q={search_query}"
                else:
                    # For other stores, use a Google search
                    search_query = f"{product_title} {store_name}".replace(" ", "+")
                    product_link = f"https://www.google.com/search?q={search_query}"
            
            product_data = {
                "title": p.get("title"),
                "price": p.get("price"),
                "link": product_link,
                "thumbnail": p.get("thumbnail"),
                "source": p.get("source")
            }
            
            if product_data["title"] and product_data["link"]:
                processed_products.append(product_data)
                print("🧾", {
                    "title": product_data["title"][:30] + "...",
                    "price": product_data["price"],
                    "link": product_data["link"][:50] + "...",
                    "source": product_data["source"]
                })

        return processed_products
    except Exception as e:
        print(f"❌ Error getting shopping items: {e}")
        return []
