from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from app.config import Config
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Set secret key from environment variable
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

    # Initialize extensions with the app
    db.init_app(app)
    migrate.init_app(app, db)

    # Register blueprints
    from app.routes import api
    app.register_blueprint(api, url_prefix='/api')

    return app
