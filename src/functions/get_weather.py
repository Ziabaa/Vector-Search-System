import requests


def get_coordinates(city: str) -> dict | None:
    url = "https://nominatim.openstreetmap.org/search"

    params = {
        "q": city,
        "format": "json",
        "limit": 1,
    }

    headers = {
        "User-Agent": "weather-app/1.0",
    }

    r = requests.get(url, params=params, headers=headers)
    data = r.json()

    if not data:
        return None

    return {
        "lat": float(data[0]["lat"]),
        "lon": float(data[0]["lon"]),
    }


def get_weather(city: str):
    coords = get_coordinates(city)

    if not coords:
        return {"error": "City not found"}

    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": coords["lat"],
        "longitude": coords["lon"],
        "current_weather": True,
    }

    return requests.get(url, params=params).json()


if __name__ == '__main__':
    city = "Kharkiv"
    res = get_weather(city)
    print(res)
