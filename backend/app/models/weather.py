from app.models.base import db, datetime

class Weather(db.Model):
    __tablename__ = 'weather_data'

    id = db.Column(db.Integer, primary_key=True)

    # "coord"
    lon = db.Column(db.Float)
    lat = db.Column(db.Float)

    # "weather" (single object in array)
    weather_id = db.Column(db.Integer)
    weather_main = db.Column(db.String(50))
    weather_description = db.Column(db.String(100))
    weather_icon = db.Column(db.String(10))

    # "base"
    base = db.Column(db.String(50))

    # "main"
    temp = db.Column(db.Float)
    feels_like = db.Column(db.Float)
    temp_min = db.Column(db.Float)
    temp_max = db.Column(db.Float)
    pressure = db.Column(db.Integer)
    humidity = db.Column(db.Integer)
    sea_level = db.Column(db.Integer)
    grnd_level = db.Column(db.Integer)

    # "visibility"
    visibility = db.Column(db.Integer)

    # "wind"
    wind_speed = db.Column(db.Float)
    wind_deg = db.Column(db.Integer)
    wind_gust = db.Column(db.Float)

    # "rain"
    rain_1h = db.Column(db.Float)

    # "clouds"
    clouds_all = db.Column(db.Integer)

    # "dt"
    dt = db.Column(db.Integer)

    # "sys"
    sys_type = db.Column(db.Integer)
    sys_id = db.Column(db.Integer)
    country = db.Column(db.String(10))
    sunrise = db.Column(db.Integer)
    sunset = db.Column(db.Integer)

    # "timezone"
    timezone = db.Column(db.Integer)

    # "id" (city ID from API)
    city_id = db.Column(db.Integer)

    # "name"
    name = db.Column(db.String(100))

    # "cod"
    cod = db.Column(db.Integer)

    # Internal
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "coord": {
                "lon": self.lon,
                "lat": self.lat
            },
            "weather": [
                {
                    "id": self.weather_id,
                    "main": self.weather_main,
                    "description": self.weather_description,
                    "icon": self.weather_icon
                }
            ],
            "base": self.base,
            "main": {
                "temp": self.temp,
                "feels_like": self.feels_like,
                "temp_min": self.temp_min,
                "temp_max": self.temp_max,
                "pressure": self.pressure,
                "humidity": self.humidity,
                "sea_level": self.sea_level,
                "grnd_level": self.grnd_level
            },
            "visibility": self.visibility,
            "wind": {
                "speed": self.wind_speed,
                "deg": self.wind_deg,
                "gust": self.wind_gust
            },
            "rain": {
                "1h": self.rain_1h
            } if self.rain_1h is not None else None,
            "clouds": {
                "all": self.clouds_all
            },
            "dt": self.dt,
            "sys": {
                "type": self.sys_type,
                "id": self.sys_id,
                "country": self.country,
                "sunrise": self.sunrise,
                "sunset": self.sunset
            },
            "timezone": self.timezone,
            "id": self.city_id,
            "name": self.name,
            "cod": self.cod,
            "created_at": self.created_at.isoformat()
        }