from flask import Flask, jsonify, send_from_directory
from flask_socketio import SocketIO
from app.config import Config
from app.models import db
from app.routes import api
from app.services.weather_service import WeatherService
from app.websockets.weather_websocket import WeatherWebSocket
from app.models.base import db
from app.models.weather import Weather
from app.models.alert import VineyardAlert
import os

# Instâncias globais
socketio = SocketIO(cors_allowed_origins="*")
weather_service = None
weather_websocket = None
__all__ = ['db', 'Weather', 'VineyardAlert']

def create_app():
    global weather_service, weather_websocket
    
    app = Flask(__name__, static_folder='static')
    app.config.from_object(Config)

    # API info (JSON apenas)
    @app.route('/')
    def api_info():
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
            "status": "🟢 Online",
            "frontend_urls": [
                "http://127.0.0.1:5000/frontend",
                "http://192.168.205.70:5000/frontend"
            ]
        })

    # Servir frontend principal
    @app.route('/frontend')
    def serve_frontend():
        try:
            return send_from_directory(app.static_folder, 'index.html')
        except Exception as e:
            return jsonify({"error": f"Frontend não encontrado: {str(e)}"}), 404
    
    # Servir arquivos estáticos do frontend (CSS, JS, etc.)
    @app.route('/frontend/<path:filename>')
    def serve_frontend_static(filename):
        try:
            return send_from_directory(app.static_folder, filename)
        except Exception as e:
            return jsonify({"error": f"Arquivo não encontrado: {filename}"}), 404

    # Rota de teste para verificar caminhos
    @app.route('/debug/paths')
    def debug_paths():
        static_path = os.path.join(app.root_path, 'static')
        return jsonify({
            "app_root_path": app.root_path,
            "static_folder": app.static_folder,
            "static_path": static_path,
            "static_exists": os.path.exists(static_path),
            "index_exists": os.path.exists(os.path.join(static_path, 'index.html')),
            "static_files": os.listdir(static_path) if os.path.exists(static_path) else "Pasta não existe"
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