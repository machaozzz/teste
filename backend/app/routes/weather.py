from flask import Blueprint, request, jsonify
from app.routes import api
from app.models import db, Weather
from app.models.alert import VineyardAlert as AlertModel
from app.services.weather_service import WeatherService
from app.services.vineyard_analyzer import VineyardAnalyzer, WeatherAnalysis
from app.services.alert_manager import AlertManager
from app import get_weather_service
from datetime import datetime, timedelta
from sqlalchemy import desc

# Instâncias dos serviços
analyzer = VineyardAnalyzer()
alert_manager = AlertManager()

@api.route('/weather/current', methods=['GET'])
def get_current_weather():
    """Obter dados meteorológicos atuais de todas as cidades"""
    try:
        city_name = request.args.get('city')
        weather_service = get_weather_service()
        
        if not weather_service:
            return jsonify({"error": "Serviço meteorológico não disponível"}), 500
        
        latest_data = weather_service.get_latest_weather(city_name)
        
        return jsonify({
            "success": True,
            "data": latest_data,
            "timestamp": datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api.route('/weather/cities', methods=['GET'])
def get_available_cities():
    """Listar cidades disponíveis para consulta"""
    try:
        weather_service = get_weather_service()
        
        if not weather_service:
            return jsonify({"error": "Serviço meteorológico não disponível"}), 500
        
        cities = [
            {
                "name": city["name"],
                "region": city["region"],
                "lat": city["lat"],
                "lon": city["lon"]
            }
            for city in weather_service.cities
        ]
        
        return jsonify({
            "success": True,
            "cities": cities
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api.route('/weather/analyze/<city_name>', methods=['GET'])
def analyze_weather_conditions(city_name):
    """Analisar condições meteorológicas para viticultura"""
    try:
        # Buscar dados atuais
        current_weather_data = Weather.query.filter_by(name=city_name)\
            .order_by(desc(Weather.created_at)).first()
        
        if not current_weather_data:
            return jsonify({"error": f"Dados não encontrados para {city_name}"}), 404
        
        # Buscar histórico recente (últimos 3 dias)
        three_days_ago = datetime.utcnow() - timedelta(days=3)
        recent_weather_data = Weather.query.filter_by(name=city_name)\
            .filter(Weather.created_at >= three_days_ago)\
            .order_by(desc(Weather.created_at)).all()
        
        # Converter para formato de análise
        current_analysis = WeatherAnalysis(
            temperature=current_weather_data.temp,
            humidity=current_weather_data.humidity,
            precipitation=current_weather_data.rain_1h or 0.0,
            wind_speed=current_weather_data.wind_speed,
            weather_condition=current_weather_data.weather_main,
            pressure=current_weather_data.pressure,
            timestamp=current_weather_data.created_at
        )
        
        recent_analyses = []
        for weather_data in recent_weather_data:
            recent_analyses.append(WeatherAnalysis(
                temperature=weather_data.temp,
                humidity=weather_data.humidity,
                precipitation=weather_data.rain_1h or 0.0,
                wind_speed=weather_data.wind_speed,
                weather_condition=weather_data.weather_main,
                pressure=weather_data.pressure,
                timestamp=weather_data.created_at
            ))
        
        # Executar análises
        alerts = analyzer.analyze_all_conditions(
            current_weather=current_analysis,
            recent_weather=recent_analyses,
            forecast_weather=recent_analyses[:5],  # Usar dados recentes como previsão
            city_id=current_weather_data.city_id,
            city_name=city_name
        )
        
        # Salvar alertas na base de dados
        saved_alerts = []
        for alert in alerts:
            saved_alert = alert_manager.save_alert(alert)
            saved_alerts.append(saved_alert.to_dict())
        
        return jsonify({
            "success": True,
            "city": city_name,
            "current_conditions": {
                "temperature": current_analysis.temperature,
                "humidity": current_analysis.humidity,
                "precipitation": current_analysis.precipitation,
                "wind_speed": current_analysis.wind_speed,
                "weather_condition": current_analysis.weather_condition,
                "timestamp": current_analysis.timestamp.isoformat()
            },
            "alerts": saved_alerts,
            "analysis_timestamp": datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api.route('/alerts', methods=['GET'])
def get_alerts():
    """Obter alertas ativos"""
    try:
        city_id = request.args.get('city_id', type=int)
        alerts = alert_manager.get_active_alerts(city_id)
        
        return jsonify({
            "success": True,
            "alerts": [alert.to_dict() for alert in alerts],
            "count": len(alerts)
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api.route('/alerts/<int:alert_id>/acknowledge', methods=['POST'])
def acknowledge_alert(alert_id):
    """Marcar alerta como reconhecido"""
    try:
        success = alert_manager.acknowledge_alert(alert_id)
        
        if success:
            return jsonify({
                "success": True,
                "message": "Alerta reconhecido com sucesso"
            })
        else:
            return jsonify({"error": "Alerta não encontrado"}), 404
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api.route('/alerts/<int:alert_id>/deactivate', methods=['POST'])
def deactivate_alert(alert_id):
    """Desativar alerta"""
    try:
        success = alert_manager.deactivate_alert(alert_id)
        
        if success:
            return jsonify({
                "success": True,
                "message": "Alerta desativado com sucesso"
            })
        else:
            return jsonify({"error": "Alerta não encontrado"}), 404
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api.route('/weather/collect', methods=['POST'])
def trigger_collection():
    """Forçar coleta de dados meteorológicos"""
    try:
        weather_service = get_weather_service()
        
        if not weather_service:
            return jsonify({"error": "Serviço meteorológico não disponível"}), 500
        
        collected_data = weather_service.collect_all_cities_data()
        
        return jsonify({
            "success": True,
            "message": f"Coleta realizada para {len(collected_data)} cidades",
            "cities_collected": [data.get('name') for data in collected_data]
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api.route('/weather/status', methods=['GET'])
def get_service_status():
    """Obter status do serviço meteorológico"""
    try:
        weather_service = get_weather_service()
        
        if not weather_service:
            return jsonify({"error": "Serviço meteorológico não disponível"}), 500
        
        # Contar registros recentes
        recent_count = Weather.query.filter(
            Weather.created_at >= datetime.utcnow() - timedelta(hours=1)
        ).count()
        
        return jsonify({
            "success": True,
            "status": {
                "collecting": weather_service.is_collecting,
                "cities_monitored": len(weather_service.cities),
                "recent_records": recent_count,
                "api_key_configured": bool(weather_service.api_key)
            }
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500