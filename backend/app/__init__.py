from flask import Flask
from flask_socketio import SocketIO
from app.config import Config
from app.models import db
from app.routes import api
from app.services.weather_service import WeatherService
from app.websockets.weather_websocket import WeatherWebSocket

# Instâncias globais
socketio = SocketIO(cors_allowed_origins="*")
weather_service = None
weather_websocket = None

def create_app():
    global weather_service, weather_websocket
    
    app = Flask(__name__)
    app.config.from_object(Config)

    # Inicializar SocketIO
    socketio.init_app(app)
    
    # Inicializar DB
    db.init_app(app)

    # Routes
    app.register_blueprint(api, url_prefix='/api')

    # Create all Tables
    with app.app_context():
        db.create_all()
        
        # Inicializar serviços
        weather_service = WeatherService()
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