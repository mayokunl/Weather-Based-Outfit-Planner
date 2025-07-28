import re

def parse_daily_outfits(gpt_response):
    """Parse GPT response to extract daily outfit search queries."""
    outfits = {}
    days = re.split(r'### Day (\d+):', gpt_response)
    
    for i in range(1, len(days), 2):
        day_num = days[i].strip()
        content = days[i + 1]
        day_label = f"Day {day_num}"
        match = re.search(r'\*\*Search Query:\*\* (.*)', content)
        outfits[day_label] = match.group(1).strip() if match else "default outfit"
    
    return outfits
