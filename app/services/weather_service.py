import requests
import os

def get_weather_summary(city, region, start_date, end_date):
    """Get weather summary for a given location and date range."""
    weather_key = os.getenv('WEATHER_API_KEY')
    
    if not weather_key:
        return "Weather API key not configured."
    
    location = f"{city},{region}"
    url = (
        "https://weather.visualcrossing.com/VisualCrossingWebServices/"
        "rest/services/timeline/"
        f"{location}/{start_date}/{end_date}"
    )
    params = {
        "unitGroup": "us",
        "key": weather_key,
        "include": "days"
    }
    
    try:
        resp = requests.get(url, params=params)
        if resp.status_code != 200:
            return "Weather data unavailable."

        data = resp.json()
        lines = []
        for day in data.get("days", []):
            date = day.get("datetime")
            high = day.get("tempmax")
            low = day.get("tempmin")
            cond = day.get("conditions")
            precip_prob = day.get("precipprob", "N/A")
            lines.append(
                f"{date}: high {high}°F, low {low}°F, {cond}"
                f" (precip chance {precip_prob}%)"
            )
        return "\n".join(lines)
    except Exception as e:
        return f"Error fetching weather data: {str(e)}"
