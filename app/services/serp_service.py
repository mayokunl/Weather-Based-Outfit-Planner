import os
from serpapi import GoogleSearch
from dotenv import load_dotenv
import json
import time
import requests
from urllib.parse import urlparse, parse_qs
import re

load_dotenv()
API_KEY = os.getenv("SERPAPI_KEY")

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
    
    search = GoogleSearch(params)
    results = search.get_dict()
    
    print("🧾 RAW IMAGE RESPONSE:")
    print(json.dumps(results, indent=2)[:1000])  # print first 1000 characters only
    
    images = results.get("images_results", [])
    print(f"📸 Found {len(images)} images for '{full_query}'")
    
    if images:
        print("🔗 First Image URL:", images[0].get("thumbnail"))
        return images[0].get("thumbnail")
    
    return None

def resolve_redirect_link(redirect_url: str, max_redirects: int = 3) -> str:
    """
    Resolve redirect links to get the actual product page URL
    """
    if not redirect_url or not redirect_url.startswith('http'):
        return redirect_url
    
    try:
        print(f"🔄 Resolving redirect: {redirect_url[:100]}...")
        
        # First, try to extract direct URL from Google redirect
        if 'google.com' in redirect_url and ('url=' in redirect_url or 'q=' in redirect_url):
            parsed = urlparse(redirect_url)
            params = parse_qs(parsed.query)
            
            # Try different parameter names that Google uses
            for param_name in ['url', 'q', 'u']:
                if param_name in params and params[param_name]:
                    direct_url = params[param_name][0]
                    if direct_url.startswith('http'):
                        print(f"✅ Extracted direct URL from redirect: {direct_url[:100]}...")
                        return direct_url
        
        # If extraction fails, follow the redirect manually
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        current_url = redirect_url
        for i in range(max_redirects):
            try:
                response = session.head(current_url, allow_redirects=False, timeout=10)
                
                if response.status_code in [301, 302, 303, 307, 308]:
                    location = response.headers.get('Location')
                    if location:
                        if location.startswith('/'):
                            # Relative URL, make it absolute
                            from urllib.parse import urljoin
                            current_url = urljoin(current_url, location)
                        else:
                            current_url = location
                        print(f"🔄 Redirect {i+1}: {current_url[:100]}...")
                    else:
                        break
                else:
                    # Final destination reached
                    print(f"✅ Final URL resolved: {current_url[:100]}...")
                    return current_url
                    
            except requests.RequestException as e:
                print(f"⚠️ Error following redirect {i+1}: {e}")
                break
        
        return current_url
        
    except Exception as e:
        print(f"❌ Error resolving redirect: {e}")
        return redirect_url

def extract_clean_product_url(raw_url: str) -> str:
    """
    Clean and extract the actual product URL from various link formats
    """
    if not raw_url:
        return None
    
    # Handle different URL patterns
    if 'amazon.com' in raw_url:
        # Clean Amazon URLs - remove tracking parameters
        if '/dp/' in raw_url:
            product_id = raw_url.split('/dp/')[1].split('/')[0].split('?')[0]
            return f"https://www.amazon.com/dp/{product_id}"
        elif '/gp/product/' in raw_url:
            product_id = raw_url.split('/gp/product/')[1].split('/')[0].split('?')[0]
            return f"https://www.amazon.com/dp/{product_id}"
    
    elif 'target.com' in raw_url:
        # Clean Target URLs
        if '/p/' in raw_url:
            return raw_url.split('?')[0]  # Remove query parameters
    
    elif 'walmart.com' in raw_url:
        # Clean Walmart URLs
        if '/ip/' in raw_url:
            return raw_url.split('?')[0]  # Remove query parameters
    
    elif 'hm.com' in raw_url:
        # H&M URLs are usually clean
        return raw_url.split('?')[0]
    
    # For other domains, try to clean common tracking parameters
    clean_url = raw_url.split('?')[0]  # Remove all query parameters
    return clean_url

def get_shopping_items(query: str, gender: str = '', num_results: int = 3) -> list[dict]:
    """Searches Google Shopping for product results with REAL working product links."""
    full_query = f"{gender} {query}".strip()
    print(f"🛍️ [Shopping] Searching: {full_query}")
    if not full_query:
        print("⚠️ Query is empty! Returning no results.")
        return []

    params = {
        "engine": "google_shopping",
        "q": full_query,
        "google_domain": "google.com",
        "hl": "en",
        "gl": "us",
        "api_key": API_KEY
    }
    print(f"📝 Params: {json.dumps(params)}")

    search = GoogleSearch(params)
    results = search.get_dict()
    print("📝 RAW SERPAPI RESPONSE (truncated):")
    print(json.dumps(results, indent=2)[:2000])

    shopping_results = results.get("shopping_results", [])
    if not shopping_results:
        print(f"⚠️ No shopping results found for query: '{full_query}'")
        if 'error' in results:
            print(f"❌ SERPAPI ERROR: {results['error']}")
    else:
        print("🔍 FIRST PRODUCT STRUCTURE:")
        first_product = shopping_results[0]
        for key, value in first_product.items():
            print(f"   {key}: {str(value)[:100]}...")

    products = shopping_results[:num_results]
    print(f"🔎 Found {len(products)} products for '{full_query}'")

    processed_products = []
    for i, product in enumerate(products):
        print(f"\n📝 Processing product {i+1}/{len(products)}: {product.get('title', 'No title')[:50]}...")

        # Try to get the best available link
        raw_link = (
            product.get("link") or 
            product.get("product_link") or 
            product.get("serpapi_product_api")
        )

        working_link = None
        purchase_options = []

        # If we have a basic link, try to resolve it
        if raw_link:
            print(f"🔗 Raw link found: {raw_link[:100]}...")

            # First, try to resolve any redirects
            resolved_link = resolve_redirect_link(raw_link)

            # Then clean the URL
            working_link = extract_clean_product_url(resolved_link)

            if working_link and working_link != raw_link:
                print(f"✅ Cleaned link: {working_link[:100]}...")

            # Add as primary purchase option
            if working_link:
                purchase_options.append({
                    "source": product.get("source", "Store"),
                    "link": working_link,
                    "price": product.get("price"),
                    "delivery": product.get("delivery"),
                    "primary": True
                })

        # Try to get additional purchase options from product API if we have product_id
        product_id = product.get("product_id")
        if product_id:
            print(f"📋 Product ID found: {product_id}, fetching additional options...")
            additional_options = get_additional_purchase_options(product_id)

            # Add additional options (avoid duplicates)
            existing_sources = {opt.get("source", "") for opt in purchase_options}
            for option in additional_options:
                if option.get("source") not in existing_sources:
                    purchase_options.append(option)

        # Create the enhanced product data
        enhanced_product = {
            "title": product.get("title"),
            "price": product.get("price"),
            "thumbnail": product.get("thumbnail"),
            "source": product.get("source"),
            "rating": product.get("rating"),
            "reviews": product.get("reviews"),
            "delivery": product.get("delivery"),
            "product_id": product_id,
            "link": working_link,  # Primary working link
            "purchase_options": purchase_options  # All available options
        }

        print(f"✅ Product processed - Primary link: {'✓' if working_link else '✗'}, Total options: {len(purchase_options)}")

        # Only include products with at least a title
        if enhanced_product.get("title"):
            processed_products.append(enhanced_product)

        # Add small delay to avoid rate limiting
        time.sleep(0.2)

    print(f"\n🏯 Processed {len(processed_products)} products total")

    # Print summary of working links
    products_with_links = sum(1 for p in processed_products if p.get('link'))
    print(f"📊 Link success rate: {products_with_links}/{len(processed_products)} products have working links")

    return processed_products

def get_additional_purchase_options(product_id: str) -> list[dict]:
    """
    Fetch additional purchase options from Google Product API
    """
    try:
        print(f"🔍 Fetching additional options for product_id: {product_id}")
        params = {
            "engine": "google_product",
            "product_id": product_id,
            "offers": "1",  # Enable fetching online sellers
            "api_key": API_KEY
        }
        search = GoogleSearch(params)
        results = search.get_dict()
        if "error" in results:
            print(f"❌ Product API Error: {results['error']}")
            return []
        sellers_results = results.get("sellers_results", {})
        online_sellers = sellers_results.get("online_sellers", [])
        print(f"🏪 Found {len(online_sellers)} additional sellers")
        purchase_options = []
        for seller in online_sellers[:3]:  # Limit to 3 additional sellers
            raw_link = seller.get("link")
            if raw_link:
                # Resolve and clean the seller link
                resolved_link = resolve_redirect_link(raw_link)
                clean_link = extract_clean_product_url(resolved_link)
                if clean_link:
                    option = {
                        "source": seller.get("name", "Store"),
                        "link": clean_link,
                        "price": seller.get("price"),
                        "delivery": seller.get("delivery"),
                        "rating": seller.get("seller_rating", {}).get("rating"),
                        "primary": False
                    }
                    purchase_options.append(option)
                    print(f"   ✅ {option['source']}: {option['price']} - {clean_link[:50]}...")
        return purchase_options
    except Exception as e:
        print(f"❌ Error fetching additional options for {product_id}: {str(e)}")
        return []

def test_link_functionality(url: str) -> bool:
    """Test if a product link is working and accessible."""
    if not url or not url.startswith('http'):
        return False
    try:
        response = requests.head(url, timeout=10, allow_redirects=True)
        is_working = response.status_code < 400
        print(f"🔍 Link test for {url[:50]}... - Status: {response.status_code} ({'✅ Working' if is_working else '❌ Broken'})")
        return is_working
    except Exception as e:
        print(f"❌ Link test failed for {url[:50]}... - Error: {e}")
        return False

def get_enhanced_shopping_items(query: str, gender: str = '', num_results: int = 3) -> list[dict]:
    """Enhanced version that includes link testing and validation."""
    products = get_shopping_items(query, gender, num_results)
    # Test links and mark their status
    for product in products:
        if product.get('link'):
            product['link_tested'] = test_link_functionality(product['link'])
        # Test purchase options too
        for option in product.get('purchase_options', []):
            if option.get('link'):
                option['link_tested'] = test_link_functionality(option['link'])
    return products