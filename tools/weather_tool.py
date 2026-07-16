import requests


class WeatherTool:

    GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"

    WEATHER_URL = "https://api.open-meteo.com/v1/forecast"

    def execute(self, location: str):

        # -------------------------
        # Step 1 : Get Coordinates
        # -------------------------

        response = requests.get(
            self.GEOCODE_URL,
            params={
                "name": location,
                "count": 1
            },
            timeout=10
        )

        response.raise_for_status()

        data = response.json()

        if "results" not in data:

            return {
                "success": False,
                "answer": f"Unable to find location '{location}'."
            }

        place = data["results"][0]

        latitude = place["latitude"]
        longitude = place["longitude"]

        # -------------------------
        # Step 2 : Weather API
        # -------------------------

        response = requests.get(
            self.WEATHER_URL,
            params={
                "latitude": latitude,
                "longitude": longitude,
                "current":
                    "temperature_2m,wind_speed_10m",
                "hourly":
                    "temperature_2m,relative_humidity_2m,wind_speed_10m"
            },
            timeout=10
        )

        response.raise_for_status()

        weather = response.json()

        current = weather["current"]

        return {

            "success": True,

            "answer": f"""
Current Weather - {place['name']}

Temperature : {current['temperature_2m']}°C

Wind Speed  : {current['wind_speed_10m']} km/h
""".strip(),

            "weather": weather
        }