from dotenv import load_dotenv
import os

load_dotenv()  # Load environment variables from .env file

class Config:
    # Database configuration
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:password@localhost:3306/mvp'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # JWT configuration
    SECRET_KEY = os.getenv('SECRET_KEY')  # Ensure you have this in your .env file
    JWT_SECRET_KEY = SECRET_KEY  # Use the same secret key for JWT
