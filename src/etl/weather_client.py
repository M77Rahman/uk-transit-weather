import requests

def get_hourly_weather(lat=51.5072, lon=-0.1276, past_days=7, forecast_days=7):
    """Hourly London weather via Open-Meteo (no API key).

    past_days/forecast_days default to 7 so the dashboard's "last 7 days"
    view has real historical data instead of only future forecast hours
    (the Open-Meteo forecast endpoint returns 0 past days by default).
    """
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat, "longitude": lon,
        "hourly": "temperature_2m,precipitation,cloudcover,windspeed_10m",
        "timezone": "Europe/London",
        "past_days": past_days,
        "forecast_days": forecast_days,
    }
    r = requests.get(url, params=params, timeout=20, headers={"User-Agent":"uk-transit-weather/1.0"})
    r.raise_for_status()
    return r.json()
