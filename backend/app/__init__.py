from flask import Flask
from app.config import Config
from app.models import db
from app.routes import api


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Inicialize DB
    db.init_app(app)

    # Routes
    app.register_blueprint(api, url_prefix='/api')

    # Create all Tables
    with app.app_context():
        db.create_all()
    #teste
    # Register error handlers, if any
    # app.register_error_handler(404, not_found_error)  
    # app.register_error_handler(500, internal_server_error)
    # Register other blueprints or extensions as needed
    return app
