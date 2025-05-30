from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum


class AlertLevel(Enum):
    """Níveis de alerta para as recomendações"""
    LOW = "baixo"
    MEDIUM = "médio"
    HIGH = "alto"
    CRITICAL = "crítico"


class AlertType(Enum):
    """Tipos de alerta para viticultura"""
    IRRIGATION = "rega"
    FUNGAL_RISK = "risco_fungos"
    HARVEST_SUGGESTION = "sugestao_colheita"
    WEATHER_WARNING = "aviso_meteorologico"


@dataclass
class VineyardAlert:
    """Classe para representar um alerta vitícola"""
    alert_type: AlertType
    level: AlertLevel
    message: str
    recommendation: str
    timestamp: datetime
    city_id: int
    city_name: str
    expires_at: Optional[datetime] = None


@dataclass
class WeatherAnalysis:
    """Análise meteorológica para viticultura"""
    temperature: float
    humidity: int
    precipitation: float
    wind_speed: float
    weather_condition: str
    pressure: int
    timestamp: datetime


class VineyardAnalyzer:
    """
    Analisador meteorológico especializado em viticultura
    
    Responsável por analisar dados meteorológicos e gerar alertas
    específicos para produtores de vinho em Portugal.
    """
    
    def __init__(self):
        # Configurações para análise vitícola
        self.config = {
            # Parâmetros para necessidade de rega
            'irrigation': {
                'temp_threshold': 25.0,  # °C - Temperatura limite
                'no_rain_days': 3,       # Dias sem chuva
                'humidity_threshold': 40  # % - Umidade baixa
            },
            
            # Parâmetros para risco de fungos
            'fungal_risk': {
                'humidity_high': 80,     # % - Umidade alta
                'temp_min': 15.0,        # °C - Temperatura mínima
                'temp_max': 25.0,        # °C - Temperatura máxima
                'consecutive_hours': 6    # Horas consecutivas
            },
            
            # Parâmetros para sugestão de colheita
            'harvest': {
                'temp_stability': 3.0,   # °C - Variação máxima
                'days_forecast': 5,      # Dias de previsão
                'ideal_temp_min': 18.0,  # °C
                'ideal_temp_max': 28.0,  # °C
                'max_wind_speed': 15.0,  # m/s
                'no_rain_required': True
            }
        }
    
    def analyze_weather_data(self, weather_data: Dict) -> WeatherAnalysis:
        """
        Converte dados meteorológicos brutos em análise estruturada
        
        Args:
            weather_data: Dados meteorológicos da API
            
        Returns:
            WeatherAnalysis: Análise estruturada
        """
        return WeatherAnalysis(
            temperature=weather_data['main']['temp'] - 273.15,  # Kelvin para Celsius
            humidity=weather_data['main']['humidity'],
            precipitation=weather_data.get('rain', {}).get('1h', 0.0),
            wind_speed=weather_data['wind']['speed'],
            weather_condition=weather_data['weather'][0]['main'],
            pressure=weather_data['main']['pressure'],
            timestamp=datetime.fromtimestamp(weather_data['dt'])
        )
    
    def check_irrigation_need(self, current_weather: WeatherAnalysis, 
                            recent_weather: List[WeatherAnalysis]) -> Optional[VineyardAlert]:
        """
        Verifica necessidade de rega
        
        Regra: Temperatura alta + Sem chuva + Humidade baixa
        
        Args:
            current_weather: Dados meteorológicos atuais
            recent_weather: Histórico recente (últimos dias)
            
        Returns:
            VineyardAlert ou None
        """
        config = self.config['irrigation']
        
        # Verificar temperatura atual
        temp_high = current_weather.temperature > config['temp_threshold']
        
        # Verificar humidade baixa
        humidity_low = current_weather.humidity < config['humidity_threshold']
        
        # Verificar dias sem chuva
        days_without_rain = 0
        for weather in recent_weather[-config['no_rain_days']:]:
            if weather.precipitation <= 0.1:  # Menos de 0.1mm considera-se sem chuva
                days_without_rain += 1
        
        no_rain_period = days_without_rain >= config['no_rain_days']
        
        if temp_high and humidity_low and no_rain_period:
            # Determinar nível de alerta
            if current_weather.temperature > 30:
                level = AlertLevel.HIGH
                message = f"Temperatura muito alta ({current_weather.temperature:.1f}°C) e {days_without_rain} dias sem chuva"
                recommendation = "Rega imediata recomendada. Regar de manhã cedo ou ao final do dia."
            else:
                level = AlertLevel.MEDIUM
                message = f"Condições secas: {current_weather.temperature:.1f}°C, {days_without_rain} dias sem chuva"
                recommendation = "Considerar rega nas próximas 24h. Verificar solo antes de regar."
            
            return VineyardAlert(
                alert_type=AlertType.IRRIGATION,
                level=level,
                message=message,
                recommendation=recommendation,
                timestamp=datetime.now(),
                city_id=0,  # Será preenchido pela chamada
                city_name="",  # Será preenchido pela chamada
                expires_at=datetime.now() + timedelta(hours=12)
            )
        
        return None
    
    def check_fungal_risk(self, current_weather: WeatherAnalysis,
                         recent_weather: List[WeatherAnalysis]) -> Optional[VineyardAlert]:
        """
        Verifica risco de doenças fúngicas
        
        Regra: Humidade alta + Temperatura amena por período prolongado
        
        Args:
            current_weather: Dados meteorológicos atuais
            recent_weather: Histórico recente
            
        Returns:
            VineyardAlert ou None
        """
        config = self.config['fungal_risk']
        
        # Condições atuais favoráveis a fungos
        humidity_high = current_weather.humidity >= config['humidity_high']
        temp_favorable = (config['temp_min'] <= current_weather.temperature <= config['temp_max'])
        
        # Verificar condições prolongadas
        favorable_hours = 0
        for weather in recent_weather[-24:]:  # Últimas 24 horas
            if (weather.humidity >= config['humidity_high'] and 
                config['temp_min'] <= weather.temperature <= config['temp_max']):
                favorable_hours += 1
        
        if humidity_high and temp_favorable and favorable_hours >= config['consecutive_hours']:
            # Determinar nível de risco
            if favorable_hours >= 12:
                level = AlertLevel.HIGH
                message = f"Risco alto de fungos: {favorable_hours}h de condições favoráveis"
                recommendation = "Aplicar fungicida preventivo. Melhorar ventilação das plantas."
            else:
                level = AlertLevel.MEDIUM
                message = f"Condições favoráveis a fungos: humidade {current_weather.humidity}%"
                recommendation = "Monitorizar plantas. Preparar tratamento preventivo se necessário."
            
            return VineyardAlert(
                alert_type=AlertType.FUNGAL_RISK,
                level=level,
                message=message,
                recommendation=recommendation,
                timestamp=datetime.now(),
                city_id=0,
                city_name="",
                expires_at=datetime.now() + timedelta(hours=24)
            )
        
        return None
    
    def check_harvest_conditions(self, current_weather: WeatherAnalysis,
                               forecast_weather: List[WeatherAnalysis]) -> Optional[VineyardAlert]:
        """
        Avalia condições para colheita
        
        Regra: Estabilidade climática + Condições ideais + Sem chuva prevista
        
        Args:
            current_weather: Dados meteorológicos atuais
            forecast_weather: Previsão meteorológica
            
        Returns:
            VineyardAlert ou None
        """
        config = self.config['harvest']
        
        # Verificar estabilidade da temperatura
        temps = [current_weather.temperature] + [w.temperature for w in forecast_weather[:config['days_forecast']]]
        temp_variation = max(temps) - min(temps)
        temp_stable = temp_variation <= config['temp_stability']
        
        # Verificar condições ideais
        temp_ideal = config['ideal_temp_min'] <= current_weather.temperature <= config['ideal_temp_max']
        wind_acceptable = current_weather.wind_speed <= config['max_wind_speed']
        
        # Verificar previsão de chuva
        no_rain_forecast = all(w.precipitation <= 0.1 for w in forecast_weather[:3])  # Próximos 3 dias
        
        # Condições gerais favoráveis
        good_conditions = (temp_stable and temp_ideal and wind_acceptable and 
                          current_weather.weather_condition in ['Clear', 'Clouds'])
        
        if good_conditions and no_rain_forecast:
            level = AlertLevel.HIGH
            message = f"Condições excelentes para colheita: {current_weather.temperature:.1f}°C, tempo estável"
            recommendation = "Janela ideal para colheita. Próximos 2-3 dias favoráveis."
        elif good_conditions:
            level = AlertLevel.MEDIUM
            message = f"Condições boas, mas chuva prevista"
            recommendation = "Considerar colheita urgente antes da chuva."
        elif temp_ideal and wind_acceptable:
            level = AlertLevel.LOW
            message = f"Condições aceitáveis para colheita"
            recommendation = "Colheita possível, mas monitorizar evolução meteorológica."
        else:
            return None
        
        return VineyardAlert(
            alert_type=AlertType.HARVEST_SUGGESTION,
            level=level,
            message=message,
            recommendation=recommendation,
            timestamp=datetime.now(),
            city_id=0,
            city_name="",
            expires_at=datetime.now() + timedelta(hours=48)
        )
    
    def analyze_all_conditions(self, current_weather: WeatherAnalysis,
                             recent_weather: List[WeatherAnalysis],
                             forecast_weather: List[WeatherAnalysis],
                             city_id: int, city_name: str) -> List[VineyardAlert]:
        """
        Executa todas as análises e retorna lista de alertas
        
        Args:
            current_weather: Dados meteorológicos atuais
            recent_weather: Histórico recente
            forecast_weather: Previsão meteorológica
            city_id: ID da cidade
            city_name: Nome da cidade
            
        Returns:
            Lista de alertas ativos
        """
        alerts = []
        
        # Verificar necessidade de rega
        irrigation_alert = self.check_irrigation_need(current_weather, recent_weather)
        if irrigation_alert:
            irrigation_alert.city_id = city_id
            irrigation_alert.city_name = city_name
            alerts.append(irrigation_alert)
        
        # Verificar risco de fungos
        fungal_alert = self.check_fungal_risk(current_weather, recent_weather)
        if fungal_alert:
            fungal_alert.city_id = city_id
            fungal_alert.city_name = city_name
            alerts.append(fungal_alert)
        
        # Verificar condições de colheita
        harvest_alert = self.check_harvest_conditions(current_weather, forecast_weather)
        if harvest_alert:
            harvest_alert.city_id = city_id
            harvest_alert.city_name = city_name
            alerts.append(harvest_alert)
        
        return alerts