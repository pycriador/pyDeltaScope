import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

basedir = Path(__file__).parent


class Config:
    """Base configuration class"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Encryption key for database passwords
    ENCRYPTION_KEY = os.environ.get('ENCRYPTION_KEY') or None
    
    # External API Configuration
    EXTERNAL_API_ENDPOINT = os.environ.get('EXTERNAL_API_ENDPOINT', '')
    EXTERNAL_API_TOKEN = os.environ.get('EXTERNAL_API_TOKEN', '')
    
    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    DATABASE_TYPE = os.environ.get('DATABASE_TYPE', 'sqlite').lower()
    
    if DATABASE_TYPE == 'sqlite':
        SQLALCHEMY_DATABASE_URI = os.environ.get('SQLITE_DB_PATH') or \
            f'sqlite:///{basedir / "instance" / "deltascope.db"}'
    else:
        # MariaDB/MySQL configuration
        DB_HOST = os.environ.get('DB_HOST', 'localhost')
        DB_PORT = os.environ.get('DB_PORT', '3306')
        DB_USER = os.environ.get('DB_USER', 'root')
        DB_PASSWORD = os.environ.get('DB_PASSWORD', '')
        DB_NAME = os.environ.get('DB_NAME', 'deltascope_db')
        
        SQLALCHEMY_DATABASE_URI = (
            f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
        )


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    DATABASE_TYPE = os.environ.get('DATABASE_TYPE', 'mariadb').lower()
    
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_PORT = os.environ.get('DB_PORT', '3306')
    DB_USER = os.environ.get('DB_USER', 'root')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', '')
    DB_NAME = os.environ.get('DB_NAME', 'deltascope_db')
    
    SQLALCHEMY_DATABASE_URI = (
        f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
    )


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}


