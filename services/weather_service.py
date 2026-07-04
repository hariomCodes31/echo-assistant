import requests


def get_weather(city):
    # Step 1: Convert city name to coordinates
    geo_url = (
        f"https://geocoding-api.open-meteo.com/v1/search"
        f"?name={city}&count=1"
    )

    geo = requests.get(geo_url).json()

    if "results" not in geo:
        return None

    lat = geo["results"][0]["latitude"]
    lon = geo["results"][0]["longitude"]

    # Step 2: Get weather
    weather_url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={lat}"
        f"&longitude={lon}"
        f"&current=temperature_2m,relative_humidity_2m,"
        f"wind_speed_10m,weather_code"
    )

    weather = requests.get(weather_url).json()

    return {
        "city": city.title(),
        "temperature": weather["current"]["temperature_2m"],
        "humidity": weather["current"]["relative_humidity_2m"],
        "wind": weather["current"]["wind_speed_10m"]
    }