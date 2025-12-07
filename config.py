import os
from datetime import timedelta #Setting the expiration time of tokens

class Config: #Base config. Other configs will inherit from this class
    """Defines config. settings for my app."""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'medi_secret'

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///hospital.db'

    SQLALCHEMY_TRACK_NOTIFICATIONS = False

    JWT_SECRTET_KEY = os.environ.get('JWR_SECRET') or 'smgmediclics'

    JWT_ACCESS_TOKEN = timedelta(hours=2)

class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False



