import requests

def get_hourly_weather(lat=51.5072, lon=-0.1276):
    """Hourly London weather via Open-Meteo (no API key)."""
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat, "longitude": lon,
        "hourly": "temperature_2m,precipitation,cloudcover,windspeed_10m",
        "timezone": "Europe/London"
    }
    r = requests.get(url, params=params, timeout=20, headers={"User-Agent":"uk-transit-weather/1.0"})
    r.raise_for_status()
    return r.json()
