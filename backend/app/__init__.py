from flask import Flask, jsonify
from flask_socketio import SocketIO
from app.config import Config
from app.models import db
from app.routes import api
from app.services.weather_service import WeatherService
from app.websockets.weather_websocket import WeatherWebSocket
from app.models.base import db
from app.models.weather import Weather
from app.models.alert import VineyardAlert

# Instâncias globais
socketio = SocketIO(cors_allowed_origins="*")
weather_service = None
weather_websocket = None
__all__ = ['db', 'Weather', 'VineyardAlert']

def create_app():
    global weather_service, weather_websocket
    
    app = Flask(__name__)
    app.config.from_object(Config)

    # Rota principal
    @app.route('/')
    def home():
        return jsonify({
            "message": "🍷 WineCast API - Sistema Meteorológico para Viticultura",
            "version": "1.0",
            "documentation": {
                "current_weather": "GET /api/weather/current",
                "cities": "GET /api/weather/cities",
                "analyze_city": "GET /api/weather/analyze/<city_name>",
                "alerts": "GET /api/alerts",
                "system_status": "GET /api/weather/status"
            },
            "status": "🟢 Online"
        })

    # Inicializar SocketIO
    socketio.init_app(app)
    
    # Inicializar DB
    db.init_app(app)

    # Routes
    app.register_blueprint(api, url_prefix='/api')

    # Create all Tables
    with app.app_context():
        db.create_all()
        
        # IMPORTANTE: Passar a instância da app para o WeatherService
        weather_service = WeatherService(app=app)
        weather_websocket = WeatherWebSocket(socketio, weather_service)
        
        # Iniciar coleta periódica (a cada 30 minutos)
        weather_service.start_periodic_collection(interval_minutes=30)

    return app

def get_weather_service():
    """Obter instância do serviço meteorológico"""
    return weather_service

def get_socketio():
    """Obter instância do SocketIO"""
    return socketio