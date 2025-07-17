# serp_utils.py
import os
from serpapi import GoogleSearch

def get_image_urls(query: str, num_results: int = 3) -> list[str]:
    """
    Fetches a list of image URLs from Google Images via SerpApi.
    """
    api_key = os.getenv("SERPAPI_KEY")
    if not api_key:
        raise EnvironmentError("SERPAPI_KEY environment variable not set")

    params = {
        "engine": "google_images",
        "q": query,
        "tbm": "isch",
        "ijn": "0",
        "api_key": api_key
    }
    search = GoogleSearch(params)
    results = search.get_dict()
    images = results.get("images_results", [])[:num_results]

    return [
        img.get("thumbnail") or img.get("original")
        for img in images
        if img.get("thumbnail") or img.get("original")
    ]