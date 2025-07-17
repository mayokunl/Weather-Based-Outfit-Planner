import os
from serpapi import GoogleSearch
from dotenv import load_dotenv

load_dotenv()

API_KEY = '198a79b4f4321d5ce1b109639730f1263080503c763471ef6ac51d9b28dcf625'
if not API_KEY:
    raise EnvironmentError("SERPAPI_KEY environment variable not set")

def get_overall_outfit_image(query: str, gender: str = '') -> str:
    """Get one image representing the full outfit (from Google Images)"""
    full_query = f"{gender} {query}".strip()
    print(f"🖼️ [Images] Searching: {full_query}")

    params = {
        "engine": "google_images",
        "q": full_query,
        "google_domain": "google.com",
        "hl": "en",
        "gl": "us",
        "api_key": API_KEY
    }

    import json

    search = GoogleSearch(params)
    results = search.get_dict()

    print("🧾 RAW SHOPPING RESPONSE:")
    print(json.dumps(results, indent=2)[:1000])  # print first 1000 characters only
    images = results.get("images_results", [])
    print(f"📸 Found {len(images)} images for '{full_query}'")

    if images:
        print("🔗 First Image URL:", images[0].get("thumbnail"))
        return images[0].get("thumbnail")

    return None


def get_shopping_items(query: str, gender: str = '', num_results: int = 3) -> list[dict]:
    """Searches Google Shopping for product results, logs results for debugging."""
    full_query = f"{gender} {query}".strip()
    print(f"🛍️ [Shopping] Searching: {full_query}")

    params = {
        "engine": "google_shopping",
        "q": full_query,
        "google_domain": "google.com",
        "hl": "en",
        "gl": "us",
        "api_key": API_KEY
    }

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