import re

def parse_daily_outfits(gpt_response, gender=None):
    """Parse GPT response to extract daily outfit details and product searches."""
    days = []
    if not gpt_response:
        return days

    # Pattern: **Day X (date): ...**
    day_pattern = re.compile(r'\*\*Day (\d+) ?(\([^)]+\))?:? ?([^\n\*]*)\*\*', re.IGNORECASE)
    product_pattern = re.compile(r'\*\*Product Searches:\*\*(.*?)(?=\n\*\*|\Z)', re.DOTALL)

    # Split by day
    day_matches = list(day_pattern.finditer(gpt_response))
    for idx, match in enumerate(day_matches):
        day_num = match.group(1)
        date = match.group(2) or ''
        title_extra = match.group(3).strip() if match.group(3) else ''
        day_title = f"Day {day_num}{' ' + date if date else ''}{': ' + title_extra if title_extra else ''}".strip()
        start = match.end()
        end = day_matches[idx + 1].start() if idx + 1 < len(day_matches) else len(gpt_response)
        day_content = gpt_response[start:end].strip()

        # Extract product searches
        product_searches = []
        prod_match = product_pattern.search(day_content)
        if prod_match:
            for line in prod_match.group(1).split('\n'):
                line = line.strip('-* ').strip()
                if line:
                    # Prefix gender if provided and not already present
                    if gender and not line.lower().startswith(gender.lower()):
                        line = f"{gender} {line}"
                    product_searches.append(line)

        days.append({
            'title': day_title,
            'content': day_content,
            # 'product_searches': product_searches  # No longer sent to template
        })
    return days

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

def remove_product_searches_section(text):
    """Remove the 'Product Searches' section and its list from markdown or HTML text."""
    return re.sub(
        r"(\*\*Product Searches:\*\*|<strong>Product Searches:</strong>)(.|\n)*?(?=(<br><br><strong>|---|$))",
        "",
        text,
        flags=re.IGNORECASE
    )