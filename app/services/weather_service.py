from datetime import datetime
import requests
import os

def get_weather_summary(city, region, start_date, end_date):
    """Get weather summary for a given location and date range (future)."""
    weather_key = os.getenv('WEATHER_API_KEY')

    if not weather_key:
        return "Weather API key not configured."

    location = f"{city},{region}"
    url = (
        f"https://weather.visualcrossing.com/VisualCrossingWebServices/"
        f"rest/services/timeline/{location}/{start_date}/{end_date}"
    )
    params = {
        "unitGroup": "us",
        "key": weather_key,
        "include": "days",
        "contentType": "json"
    }

    print(f"📡 Requesting URL: {url} with params: {params}")

    try:
        # Check if forecast date range exceeds 15 days from today
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        today = datetime.today()
        forecast_days = (start_dt - today).days
        if forecast_days > 15:
            print("⚠️ Forecast is beyond 15-day range. Data may be historical averages.")

        resp = requests.get(url, params=params)
        if resp.status_code != 200:
            return f"Weather data unavailable: {resp.text}"

        data = resp.json()
        lines = []
        for day in data.get("days", []):
            date = day.get("datetime")
            high = day.get("tempmax")
            low = day.get("tempmin")
            cond = day.get("conditions")
            precip_prob = day.get("precipprob", "N/A")
            source = day.get("source", "unknown")
            # Distinguish if data is from forecast or historical norms
            source_note = " (historical average)" if "normal" in str(source).lower() else ""
            lines.append(
                f"{date}: high {high}°F, low {low}°F, {cond} (precip chance {precip_prob}%)"
                f"{source_note}"
            )
        return "\n".join(lines)
    except Exception as e:
        return f"Error fetching weather data: {str(e)}"
