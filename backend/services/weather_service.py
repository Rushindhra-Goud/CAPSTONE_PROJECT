"""
Weather service -- fetches live weather from OpenWeatherMap free tier.
Sign up free at https://openweathermap.org/api to get OWM_API_KEY,
then put it in your .env file.
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

OWM_API_KEY = os.getenv("OWM_API_KEY")
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

# Maps OpenWeatherMap's condition names to the exact categories used
# in the dataset's weather_condition column.
CONDITION_MAP = {
    "Clear": "Clear",
    "Clouds": "Cloudy",
    "Rain": "Moderate Rain",
    "Drizzle": "Light Rain",
    "Thunderstorm": "Heavy Rain",
    "Mist": "Fog",
    "Fog": "Fog",
    "Haze": "Fog",
}


def get_live_weather(city: str = "Warangal") -> str:
    """
    Returns a weather_condition string matching the dataset's categories:
    Clear, Cloudy, Light Rain, Moderate Rain, Heavy Rain, Fog.
    Falls back to "Clear" if the API key isn't set yet or the call fails,
    so the rest of the app keeps working during early development.
    """
    if not OWM_API_KEY:
        return "Clear"

    try:
        params = {"q": city, "appid": OWM_API_KEY, "units": "metric"}
        resp = requests.get(BASE_URL, params=params, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        condition = data["weather"][0]["main"]
        return CONDITION_MAP.get(condition, "Clear")
    except Exception:
        return "Clear"
