import random
from datetime import datetime, timedelta
from faker import Faker
import json


class WeatherDataFactory:
    def __init__(self):
        self.fake = Faker()
        self.weather_types = [
            {"id": 200, "main": "Thunderstorm", "description": "thunderstorm with light rain", "icon": "11d"},
            {"id": 300, "main": "Drizzle", "description": "light intensity drizzle", "icon": "09d"},
            {"id": 500, "main": "Rain", "description": "light rain", "icon": "10d"},
            {"id": 501, "main": "Rain", "description": "moderate rain", "icon": "10d"},
            {"id": 600, "main": "Snow", "description": "light snow", "icon": "13d"},
            {"id": 701, "main": "Mist", "description": "mist", "icon": "50d"},
            {"id": 800, "main": "Clear", "description": "clear sky", "icon": "01d"},
            {"id": 801, "main": "Clouds", "description": "few clouds", "icon": "02d"},
            {"id": 802, "main": "Clouds", "description": "scattered clouds", "icon": "03d"},
            {"id": 803, "main": "Clouds", "description": "broken clouds", "icon": "04d"},
            {"id": 804, "main": "Clouds", "description": "overcast clouds", "icon": "04d"}
        ]

        self.cities = [
            # 🍷 Good wine regions (warm, dry inland)
            {"id": 1, "name": "Peso da Régua", "country": "PT", "lat": 41.16, "lon": -7.78, "wine_quality": "good"},
            # Douro
            {"id": 2, "name": "Évora", "country": "PT", "lat": 38.57, "lon": -7.91, "wine_quality": "good"},  # Alentejo
            {"id": 3, "name": "Reguengos de Monsaraz", "country": "PT", "lat": 38.42, "lon": -7.54,
             "wine_quality": "good"},
            {"id": 4, "name": "Palmela", "country": "PT", "lat": 38.57, "lon": -8.90, "wine_quality": "good"},
            # Setúbal

            # ❌ Bad wine regions (coastal, rainy, urban)
            {"id": 5, "name": "Porto", "country": "PT", "lat": 41.15, "lon": -8.61, "wine_quality": "bad"},
            {"id": 6, "name": "Lisbon", "country": "PT", "lat": 38.72, "lon": -9.14, "wine_quality": "bad"},
            {"id": 7, "name": "Braga", "country": "PT", "lat": 41.55, "lon": -8.42, "wine_quality": "bad"}
        ]

    def generate_weather_data(self, city=None, days_ago=0):
        """Generate a single weather record"""
        if not city:
            city = random.choice(self.cities)

        weather_type = self._weighted_weather_choice(city)
        record_time = datetime.utcnow() - timedelta(days=days_ago)

        base_data = {
            "coord": {"lon": city["lon"], "lat": city["lat"]},
            "weather": [weather_type],
            "base": "stations",
            "main": self._generate_main_data(weather_type, city),
            "visibility": random.randint(1000, 10000),
            "wind": self._generate_wind_data(weather_type),
            "clouds": {"all": random.randint(0, 100)},
            "dt": int(record_time.timestamp()),
            "sys": self._generate_sys_data(city, record_time),
            "timezone": self._generate_timezone(city),
            "id": city["id"],
            "name": city["name"],
            "cod": 200
        }

        # Add precipitation Data if exists
        if weather_type["main"] in ["Rain", "Drizzle"]:
            base_data["rain"] = {"1h": round(random.uniform(0.1, 5.0), 2)}
        elif weather_type["main"] == "Snow":
            base_data["snow"] = {"1h": round(random.uniform(0.1, 3.0), 2)}
        elif weather_type["main"] == "Thunderstorm":
            base_data["rain"] = {"1h": round(random.uniform(2.0, 15.0), 2)}

        return base_data

    def _weighted_weather_choice(self, city):
        """Generate weather with location-appropriate weights"""
        weights = {
            "PT": [0.05, 0.05, 0.1, 0.15, 0.01, 0.05, 0.3, 0.15, 0.08, 0.04, 0.02]  # Portugal: lots of sun & some rain
        }

        country_weights = weights.get(city["country"], weights["US"])
        return random.choices(self.weather_types, weights=country_weights, k=1)[0]

    def _generate_main_data(self, weather_type, city):
        """Generate realistic main weather data based on location and weather type"""
        base_temp = self._get_base_temp(city)
        temp_variation = {
            "Thunderstorm": (-5, 3),
            "Drizzle": (-2, 2),
            "Rain": (-3, 1),
            "Snow": (-15, -5),
            "Mist": (-1, 1),
            "Clear": (0, 5),
            "Clouds": (-2, 3)
        }.get(weather_type["main"], (0, 0))

        temp = base_temp + random.uniform(*temp_variation)
        return {
            "temp": round(temp, 2),
            "feels_like": round(temp + random.uniform(-3, 0), 2),
            "temp_min": round(temp + random.uniform(-5, -1), 2),
            "temp_max": round(temp + random.uniform(1, 5), 2),
            "pressure": random.randint(950, 1050),
            "humidity": random.randint(30, 100),
            "sea_level": random.randint(950, 1050),
            "grnd_level": random.randint(900, 1000)
        }

    def _get_base_temp(self, city):
        """Get base temperature based on city location and season"""
        northern = city["lat"] > 0
        now = datetime.now()
        month = now.month

        if northern:
            # Northern hemisphere seasons
            if month in [12, 1, 2]:  # Winter
                return random.uniform(250, 280)
            elif month in [3, 4, 5]:  # Spring
                return random.uniform(280, 295)
            elif month in [6, 7, 8]:  # Summer
                return random.uniform(295, 310)
            else:  # Fall
                return random.uniform(280, 295)
        else:
            # Southern hemisphere (reversed seasons)
            if month in [12, 1, 2]:  # Summer
                return random.uniform(295, 310)
            elif month in [3, 4, 5]:  # Fall
                return random.uniform(280, 295)
            elif month in [6, 7, 8]:  # Winter
                return random.uniform(250, 280)
            else:  # Spring
                return random.uniform(280, 295)

    def _generate_wind_data(self, weather_type):
        """Generate wind data based on weather type"""
        base_speed = {
            "Thunderstorm": random.uniform(10, 25),
            "Drizzle": random.uniform(2, 8),
            "Rain": random.uniform(5, 15),
            "Snow": random.uniform(3, 10),
            "Mist": random.uniform(0, 3),
            "Clear": random.uniform(1, 5),
            "Clouds": random.uniform(2, 8)
        }.get(weather_type["main"], random.uniform(0, 5))

        return {
            "speed": round(base_speed, 2),
            "deg": random.randint(0, 359),
            "gust": round(base_speed * random.uniform(1.2, 2.0), 2)
        }

    def _generate_sys_data(self, city, record_time):
        # Simplified calculation - in reality you'd use proper astronomical formulas
        daylight_hours = 8 + 6 * (abs(city["lat"]) / 90)  # More daylight near poles in summer
        sunrise = record_time - timedelta(hours=daylight_hours / 2)
        sunset = record_time + timedelta(hours=daylight_hours / 2)

        return {
            "type": random.randint(1, 3),
            "id": random.randint(1000, 9999),
            "country": city["country"],
            "sunrise": int(sunrise.timestamp()),
            "sunset": int(sunset.timestamp())
        }

    def _generate_timezone(self, city):
        """Generate timezone offset based on longitude"""
        # Simplified timezone calculation (1 hour per 15 degrees)
        return int(city["lon"] / 15) * 3600

    def generate_forecast(self, city_id, days=5, records_per_day=8):
        """Generate a multi-day forecast for a city"""
        city = next((c for c in self.cities if c["id"] == city_id), None)
        if not city:
            raise ValueError(f"City with ID {city_id} not found")

        forecast = []
        for day in range(days):
            for hour in range(0, 24, 24 // records_per_day):
                time_offset = timedelta(days=day, hours=hour)
                forecast.append(self.generate_weather_data(
                    city=city,
                    days_ago=-day  # Negative for future dates
                ))
        return forecast