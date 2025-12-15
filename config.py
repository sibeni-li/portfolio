import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base config - shared settings"""
    SECRET_KEY = os.getenv("SECRET_KEY")
    SESSION_PERMANENT = False
    SESSION_TYPE = "filesystem"
    ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")
    LOG_FILE = 'app.log'
    LOG_LEVEL = 'ERROR'
    REDIS_URL = os.getenv("REDIS_URL", "memory://")

class DevelopmentConfig(Config):
    """Development-specific settings"""
    DEBUG = True

class ProductionConfig(Config):
    """Production-specific settings"""
    DEBUG = False
