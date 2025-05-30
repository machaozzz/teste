from app.factories.weather_factory import WeatherDataFactory
from app.models import db, Weather
from app import create_app


def populate_database():
    app = create_app()
    factory = WeatherDataFactory()

    with app.app_context():

        # Generate current weather for all cities
        for city in factory.cities:
            weather_data = factory.generate_weather_data(city=city)
            weather = Weather(
                city_id=weather_data["id"],
                name=weather_data["name"],
                coord=weather_data["coord"],
                weather=weather_data["weather"],
                base=weather_data["base"],
                main=weather_data["main"],
                visibility=weather_data["visibility"],
                wind=weather_data["wind"],
                rain=weather_data.get("rain"),
                snow=weather_data.get("snow"),
                clouds=weather_data["clouds"],
                dt=weather_data["dt"],
                sys=weather_data["sys"],
                timezone=weather_data["timezone"],
                cod=weather_data["cod"]
            )
            db.session.add(weather)

        # Generate historical data (past 7 days) for each city
        for city in factory.cities:
            for days_ago in range(1, 8):
                weather_data = factory.generate_weather_data(city=city, days_ago=days_ago)
                weather = Weather(
                    city_id=weather_data["id"],
                    name=weather_data["name"],
                    coord=weather_data["coord"],
                    weather=weather_data["weather"],
                    base=weather_data["base"],
                    main=weather_data["main"],
                    visibility=weather_data["visibility"],
                    wind=weather_data["wind"],
                    rain=weather_data.get("rain"),
                    snow=weather_data.get("snow"),
                    clouds=weather_data["clouds"],
                    dt=weather_data["dt"],
                    sys=weather_data["sys"],
                    timezone=weather_data["timezone"],
                    cod=weather_data["cod"]
                )
                db.session.add(weather)

        db.session.commit()
        print(f"Successfully populated database with weather data")


if __name__ == '__main__':
    populate_database()