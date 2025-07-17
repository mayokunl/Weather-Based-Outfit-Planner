import requests
import os

weather_key = os.getenv('WEATHER_API_KEY')

def get_weather_summary(city, region, start_date, end_date):
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
    resp = requests.get(url, params=params)
    if resp.status_code != 200:
        return "Weather data unavailable."

    data = resp.json()
    lines = []
    for day in data.get("days", []):
        date        = day.get("datetime")
        high        = day.get("tempmax")
        low         = day.get("tempmin")
        cond        = day.get("conditions")
        precip_prob = day.get("precipprob", "N/A")
        lines.append(
            f"{date}: high {high}°F, low {low}°F, {cond}"
            f" (precip chance {precip_prob}%)"
        )
    return "\n".join(lines)
