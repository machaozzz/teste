import os
from dotenv import load_dotenv

# Carregar variáveis do ficheiro .env
load_dotenv()

class Config:
    # Base de dados MySQL
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'mysql+pymysql://root:admin123@localhost/winecast_db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Chave secreta do Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Configurações do SocketIO
    SOCKETIO_ASYNC_MODE = 'eventlet'