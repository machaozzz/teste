from flask import Blueprint, request, jsonify
from app.models import db, Weather

# Create  Blueprints

api = Blueprint('api', __name__)