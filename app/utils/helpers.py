import re

def parse_daily_outfits(gpt_response):
    """Parse GPT response to extract daily outfit search queries."""
    outfits = {}
    
    # Try multiple parsing patterns to be more robust
    
    # Pattern 1: ### Day 1: format
    days = re.split(r'### Day (\d+):', gpt_response)
    if len(days) > 2:  # Found matches
        for i in range(1, len(days), 2):
            day_num = days[i].strip()
            content = days[i + 1]
            day_label = f"Day {day_num}"
            match = re.search(r'\*\*Search Query:\*\*\s*(.*)', content)
            outfits[day_label] = match.group(1).strip() if match else f"summer outfit day {day_num}"
        return outfits
    
    # Pattern 2: Day 1: format (without ###)
    days = re.split(r'Day (\d+):', gpt_response)
    if len(days) > 2:  # Found matches
        for i in range(1, len(days), 2):
            day_num = days[i].strip()
            content = days[i + 1]
            day_label = f"Day {day_num}"
            
            # Try to find search queries or product searches
            search_match = re.search(r'(?:Search Query|Product Searches?):\*?\*?\s*(.*?)(?:\n|$)', content, re.IGNORECASE)
            if search_match:
                outfits[day_label] = search_match.group(1).strip()
            else:
                # Fall back to extracting clothing items from content
                clothing_items = extract_clothing_items(content)
                outfits[day_label] = ", ".join(clothing_items) if clothing_items else f"summer outfit day {day_num}"
        return outfits
    
    # Pattern 3: No clear day structure, create default
    outfits["Day 1"] = "summer casual outfit"
    return outfits

def extract_clothing_items(content):
    """Extract clothing items from unstructured content."""
    items = []
    
    # Common clothing keywords
    clothing_patterns = [
        r'(t-shirt|tank top|blouse|shirt|top)',
        r'(shorts|pants|jeans|dress|skirt)',
        r'(sandals|sneakers|shoes|boots)',
        r'(hat|sunglasses|bag|jacket)'
    ]
    
    for pattern in clothing_patterns:
        matches = re.findall(pattern, content.lower())
        items.extend(matches)
    
    return list(set(items))  # Remove duplicates
