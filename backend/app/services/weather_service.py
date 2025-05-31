import requests
import os
from datetime import datetime, timedelta
from app.models import db, Weather
import threading
import time
from typing import Dict, List, Optional
from flask import current_app

class WeatherService:
    """
    Serviço responsável por coletar dados meteorológicos da OpenWeatherMap API
    e armazenar na base de dados.
    """
    
    def __init__(self, app=None):
        self.api_key = os.getenv('OPENWEATHER_API_KEY')
        self.base_url = "http://api.openweathermap.org/data/2.5/weather"
        self.is_collecting = False
        self._observers = []
        self.app = app
        
        # Cidades portuguesas para vindimas
        self.cities = [
            {"name": "Peso da Régua", "lat": 41.16, "lon": -7.78, "region": "Douro"},
            {"name": "Évora", "lat": 38.57, "lon": -7.91, "region": "Alentejo"},
            {"name": "Reguengos de Monsaraz", "lat": 38.42, "lon": -7.54, "region": "Alentejo"},
            {"name": "Palmela", "lat": 38.57, "lon": -8.90, "region": "Setúbal"},
            {"name": "Porto", "lat": 41.15, "lon": -8.61, "region": "Vinho Verde"},
            {"name": "Lisbon", "lat": 38.72, "lon": -9.14, "region": "Lisboa"},
            {"name": "Braga", "lat": 41.55, "lon": -8.42, "region": "Vinho Verde"}
        ]
    
    def add_observer(self, observer):
        """Adicionar observador para notificações (Observer Pattern)"""
        self._observers.append(observer)
    
    def remove_observer(self, observer):
        """Remover observador"""
        if observer in self._observers:
            self._observers.remove(observer)
    
    def notify_observers(self, data: Dict):
        """Notificar todos os observadores sobre novos dados"""
        for observer in self._observers:
            observer.update(data)
    
    def fetch_weather_data(self, city: Dict) -> Optional[Dict]:
        """
        Buscar dados meteorológicos para uma cidade específica
        
        Args:
            city (Dict): Dicionário com informações da cidade
            
        Returns:
            Optional[Dict]: Dados meteorológicos ou None se erro
        """
        try:
            params = {
                'lat': city['lat'],
                'lon': city['lon'],
                'appid': self.api_key,
                'units': 'metric',  # Celsius
                'lang': 'pt'
            }
            
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            data['region'] = city['region']  # Adicionar região
            
            return data
            
        except requests.exceptions.RequestException as e:
            print(f"Erro ao buscar dados para {city['name']}: {e}")
            return None
        except Exception as e:
            print(f"Erro inesperado para {city['name']}: {e}")
            return None
    
    def save_weather_to_db(self, weather_data: Dict) -> bool:
        """
        Salvar dados meteorológicos na base de dados
        
        Args:
            weather_data (Dict): Dados da API OpenWeatherMap
            
        Returns:
            bool: True se salvou com sucesso, False caso contrário
        """
        try:
            # Extrair dados do JSON da API
            weather_info = weather_data['weather'][0] if weather_data.get('weather') else {}
            main_data = weather_data.get('main', {})
            wind_data = weather_data.get('wind', {})
            clouds_data = weather_data.get('clouds', {})
            rain_data = weather_data.get('rain', {})
            sys_data = weather_data.get('sys', {})
            coord_data = weather_data.get('coord', {})
            
            weather = Weather(
                # Coordenadas
                lon=coord_data.get('lon'),
                lat=coord_data.get('lat'),
                
                # Informações do tempo
                weather_id=weather_info.get('id'),
                weather_main=weather_info.get('main'),
                weather_description=weather_info.get('description'),
                weather_icon=weather_info.get('icon'),
                
                # Base
                base=weather_data.get('base'),
                
                # Dados principais
                temp=main_data.get('temp'),
                feels_like=main_data.get('feels_like'),
                temp_min=main_data.get('temp_min'),
                temp_max=main_data.get('temp_max'),
                pressure=main_data.get('pressure'),
                humidity=main_data.get('humidity'),
                sea_level=main_data.get('sea_level'),
                grnd_level=main_data.get('grnd_level'),
                
                # Visibilidade
                visibility=weather_data.get('visibility'),
                
                # Vento
                wind_speed=wind_data.get('speed'),
                wind_deg=wind_data.get('deg'),
                wind_gust=wind_data.get('gust'),
                
                # Chuva
                rain_1h=rain_data.get('1h'),
                
                # Nuvens
                clouds_all=clouds_data.get('all'),
                
                # Timestamp
                dt=weather_data.get('dt'),
                
                # Sistema
                sys_type=sys_data.get('type'),
                sys_id=sys_data.get('id'),
                country=sys_data.get('country'),
                sunrise=sys_data.get('sunrise'),
                sunset=sys_data.get('sunset'),
                
                # Timezone
                timezone=weather_data.get('timezone'),
                
                # ID e nome da cidade
                city_id=weather_data.get('id'),
                name=weather_data.get('name'),
                
                # Código
                cod=weather_data.get('cod')
            )
            
            db.session.add(weather)
            db.session.commit()
            
            print(f"Dados salvos para {weather_data.get('name')}")
            return True
            
        except Exception as e:
            print(f"Erro ao salvar dados na BD: {e}")
            db.session.rollback()
            return False
    
    def collect_all_cities_data(self):
        """Coletar dados para todas as cidades"""
        collected_data = []
        
        for city in self.cities:
            weather_data = self.fetch_weather_data(city)
            if weather_data:
                success = self.save_weather_to_db(weather_data)
                if success:
                    collected_data.append(weather_data)
                    # Notificar observadores
                    self.notify_observers({
                        'type': 'weather_update',
                        'city': city['name'],
                        'data': weather_data,
                        'timestamp': datetime.utcnow().isoformat()
                    })
        
        return collected_data
    
    def start_periodic_collection(self, interval_minutes: int = 30):
        """
        Iniciar coleta periódica de dados
        
        Args:
            interval_minutes (int): Intervalo em minutos entre coletas
        """
        if self.is_collecting:
            print("Coleta já está em execução")
            return
        
        self.is_collecting = True
        
        def collect_loop():
            while self.is_collecting:
                try:
                    print(f"Iniciando coleta de dados - {datetime.now()}")
                    
                    # IMPORTANTE: Usar o contexto da aplicação na thread
                    with self.app.app_context():
                        self.collect_all_cities_data()
                    
                    print(f"Coleta concluída - {datetime.now()}")
                    
                    # Aguardar próximo ciclo
                    time.sleep(interval_minutes * 60)
                    
                except Exception as e:
                    print(f"Erro na coleta periódica: {e}")
                    time.sleep(60)  # Aguardar 1 minuto antes de tentar novamente
        
        # Executar em thread separada
        collection_thread = threading.Thread(target=collect_loop, daemon=True)
        collection_thread.start()
        
        print(f"Coleta periódica iniciada (intervalo: {interval_minutes} minutos)")
    
    def stop_periodic_collection(self):
        """Parar coleta periódica"""
        self.is_collecting = False
        print("Coleta periódica parada")
    
    def get_latest_weather(self, city_name: str = None) -> List[Dict]:
        """
        Obter dados meteorológicos mais recentes
        
        Args:
            city_name (str, optional): Nome da cidade específica
            
        Returns:
            List[Dict]: Lista de dados meteorológicos
        """
        try:
            query = Weather.query
            
            if city_name:
                query = query.filter_by(name=city_name)
            
            # Obter registros mais recentes (últimas 24 horas)
            yesterday = datetime.utcnow() - timedelta(hours=24)
            query = query.filter(Weather.created_at >= yesterday)
            
            # Ordenar por data de criação (mais recente primeiro)
            weather_records = query.order_by(Weather.created_at.desc()).all()
            
            return [record.to_dict() for record in weather_records]
            
        except Exception as e:
            print(f"Erro ao buscar dados da BD: {e}")
            return []