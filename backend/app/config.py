import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'mysql+pymysql://user:password@localhost/database_name')
    SECRET_KEY = os.getenv('SECRET_KEY', '')