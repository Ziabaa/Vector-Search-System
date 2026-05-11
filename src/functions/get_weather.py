import requests

from src.functions.base.param import Param, CityParam
from src.functions.base.tool import BaseTool


class GetWeather(BaseTool):
    """
    Get current weather by city.
    """
    name = "GetWeather"
    params: list[Param] = [CityParam()]

    @staticmethod
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

        response = requests.get(
            url,
            params=params,
            headers=headers,
        )

        data = response.json()

        if not data:
            return None

        return {
            "lat": float(data[0]["lat"]),
            "lon": float(data[0]["lon"]),
        }

    @staticmethod
    def get_wind_direction(deg: float) -> str:
        directions = [
            "Північний",
            "Північно-східний",
            "Східний",
            "Південно-східний",
            "Південний",
            "Південно-західний",
            "Західний",
            "Північно-західний",
        ]

        index = round(deg / 45) % 8

        return directions[index]

    def execute(self) -> str:
        city = self.params[0].value

        coords = self.get_coordinates(city)

        if not coords:
            return "Місто не знайдено"

        url = "https://api.open-meteo.com/v1/forecast"

        params = {
            "latitude": coords["lat"],
            "longitude": coords["lon"],
            "current_weather": True,
        }

        weather = requests.get(url, params=params).json()

        current = weather["current_weather"]

        wind_direction = self.get_wind_direction(
            current["winddirection"],
        )

        lines = [
            f"Поточна погода у місті {city}:",
            f"Температура:      {current['temperature']} °C",
            f"Швидкість вітру:  {current['windspeed']} км/год",
            f"Напрям вітру:     {wind_direction}",
            f"Час оновлення:    {current['time']}",
        ]

        return "\n".join(lines)


if __name__ == '__main__':
    tool = GetWeather()
    for tool_param in tool.params:
        if tool_param.name == 'city':
            tool_param.value = 'Kharkiv'
    print(tool.execute())
