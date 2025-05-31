from flask import Blueprint, request, jsonify
from app.models import db, Weather

# Create  Blueprints
api = Blueprint('api', __name__)

# Adicionar rota principal
@api.route('/', methods=['GET'])
def home():
    """Página inicial da API"""
    return jsonify({
        "message": "WineCast API - Sistema Meteorológico para Viticultura",
        "version": "1.0",
        "endpoints": {
            "weather_current": "/api/weather/current",
            "weather_cities": "/api/weather/cities", 
            "weather_analyze": "/api/weather/analyze/<city_name>",
            "alerts": "/api/alerts",
            "weather_status": "/api/weather/status"
        },
        "status": "online"
    })