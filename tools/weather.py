from services.weather_service import get_weather


def weather(command):

    city = command.lower().replace("weather in", "").strip()

    data = get_weather(city)

    if data is None:
        return "❌ City not found."

    return f"""
🌤 Weather in {data['city']}

🌡 Temperature : {data['temperature']}°C
💧 Humidity    : {data['humidity']}%
🌬 Wind Speed  : {data['wind']} km/h
"""