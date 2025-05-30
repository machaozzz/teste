import sys
import os

# Adicionar o diretório backend ao path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from app.factories.weather_factory import WeatherDataFactory
from app.models import db, Weather
from app import create_app


def populate_database():
    """Popular a base de dados com dados meteorológicos simulados"""
    app = create_app()
    factory = WeatherDataFactory()

    with app.app_context():
        print("Iniciando população da base de dados...")
        
        # Limpar dados existentes (opcional)
        # Weather.query.delete()
        # db.session.commit()

        # Gerar dados atuais para todas as cidades
        print("Gerando dados atuais...")
        for city in factory.cities:
            weather_data = factory.generate_weather_data(city=city)
            
            # Extrair dados do JSON gerado
            weather_info = weather_data['weather'][0]
            main_data = weather_data['main']
            wind_data = weather_data['wind']
            clouds_data = weather_data['clouds']
            rain_data = weather_data.get('rain', {})
            sys_data = weather_data['sys']
            coord_data = weather_data['coord']
            
            weather = Weather(
                # Coordenadas
                lon=coord_data['lon'],
                lat=coord_data['lat'],
                
                # Informações do tempo
                weather_id=weather_info['id'],
                weather_main=weather_info['main'],
                weather_description=weather_info['description'],
                weather_icon=weather_info['icon'],
                
                # Base
                base=weather_data['base'],
                
                # Dados principais
                temp=main_data['temp'],
                feels_like=main_data['feels_like'],
                temp_min=main_data['temp_min'],
                temp_max=main_data['temp_max'],
                pressure=main_data['pressure'],
                humidity=main_data['humidity'],
                sea_level=main_data.get('sea_level'),
                grnd_level=main_data.get('grnd_level'),
                
                # Visibilidade
                visibility=weather_data['visibility'],
                
                # Vento
                wind_speed=wind_data['speed'],
                wind_deg=wind_data['deg'],
                wind_gust=wind_data.get('gust'),
                
                # Chuva
                rain_1h=rain_data.get('1h'),
                
                # Nuvens
                clouds_all=clouds_data['all'],
                
                # Timestamp
                dt=weather_data['dt'],
                
                # Sistema
                sys_type=sys_data['type'],
                sys_id=sys_data['id'],
                country=sys_data['country'],
                sunrise=sys_data['sunrise'],
                sunset=sys_data['sunset'],
                
                # Timezone
                timezone=weather_data['timezone'],
                
                # ID e nome da cidade
                city_id=weather_data['id'],
                name=weather_data['name'],
                
                # Código
                cod=weather_data['cod']
            )
            
            db.session.add(weather)
            print(f"Dados atuais adicionados para {city['name']}")

        # Gerar dados históricos (últimos 7 dias) para cada cidade
        print("Gerando dados históricos...")
        for city in factory.cities:
            for days_ago in range(1, 8):
                weather_data = factory.generate_weather_data(city=city, days_ago=days_ago)
                
                # Extrair dados do JSON gerado
                weather_info = weather_data['weather'][0]
                main_data = weather_data['main']
                wind_data = weather_data['wind']
                clouds_data = weather_data['clouds']
                rain_data = weather_data.get('rain', {})
                sys_data = weather_data['sys']
                coord_data = weather_data['coord']
                
                weather = Weather(
                    # Coordenadas
                    lon=coord_data['lon'],
                    lat=coord_data['lat'],
                    
                    # Informações do tempo
                    weather_id=weather_info['id'],
                    weather_main=weather_info['main'],
                    weather_description=weather_info['description'],
                    weather_icon=weather_info['icon'],
                    
                    # Base
                    base=weather_data['base'],
                    
                    # Dados principais
                    temp=main_data['temp'],
                    feels_like=main_data['feels_like'],
                    temp_min=main_data['temp_min'],
                    temp_max=main_data['temp_max'],
                    pressure=main_data['pressure'],
                    humidity=main_data['humidity'],
                    sea_level=main_data.get('sea_level'),
                    grnd_level=main_data.get('grnd_level'),
                    
                    # Visibilidade
                    visibility=weather_data['visibility'],
                    
                    # Vento
                    wind_speed=wind_data['speed'],
                    wind_deg=wind_data['deg'],
                    wind_gust=wind_data.get('gust'),
                    
                    # Chuva
                    rain_1h=rain_data.get('1h'),
                    
                    # Nuvens
                    clouds_all=clouds_data['all'],
                    
                    # Timestamp
                    dt=weather_data['dt'],
                    
                    # Sistema
                    sys_type=sys_data['type'],
                    sys_id=sys_data['id'],
                    country=sys_data['country'],
                    sunrise=sys_data['sunrise'],
                    sunset=sys_data['sunset'],
                    
                    # Timezone
                    timezone=weather_data['timezone'],
                    
                    # ID e nome da cidade
                    city_id=weather_data['id'],
                    name=weather_data['name'],
                    
                    # Código
                    cod=weather_data['cod']
                )
                
                db.session.add(weather)
            
            print(f"Dados históricos adicionados para {city['name']}")

        # Confirmar todas as alterações
        db.session.commit()
        
        # Contar registros criados
        total_records = Weather.query.count()
        print(f"Base de dados populada com sucesso!")
        print(f"Total de registros: {total_records}")
        print(f"Cidades: {len(factory.cities)}")
        print(f"Registros por cidade: {total_records // len(factory.cities)}")


if __name__ == '__main__':
    populate_database()