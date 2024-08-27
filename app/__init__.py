from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from .config import Config
from flask_cors import CORS

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app, resources = {r"/*": {"origins": "http://10.0.0.171:8080"}})


    
    db.init_app(app)
    
    JWTManager(app)  # Initialize JWT Manager without assigning to a variable
    
    with app.app_context():
        from .routes import api  # Import routes
        app.register_blueprint(api)
        db.create_all()  # Create tables if they don't exist
        
    return app
