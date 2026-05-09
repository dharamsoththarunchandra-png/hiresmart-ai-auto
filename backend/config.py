import os
from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv

base_dir = Path(__file__).resolve().parent
load_dotenv(base_dir / '.env')


def _fix_db_url(url: str) -> str:
    """Render gives postgres:// but SQLAlchemy 1.4+ requires postgresql://."""
    if url and url.startswith('postgres://'):
        return url.replace('postgres://', 'postgresql://', 1)
    return url


class Config:
    """Base configuration for HireSmart."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'change-me-in-production')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'change-me-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(seconds=int(os.environ.get('JWT_ACCESS_TOKEN_EXPIRES', 3600)))
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', str(base_dir / 'uploads'))
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 52428800))  # 50MB
    ALLOWED_EXTENSIONS = {ext.strip().lower() for ext in os.environ.get('ALLOWED_EXTENSIONS', 'pdf,doc,docx').split(',')}
    CORS_HEADERS = 'Content-Type'
    RATELIMIT_HEADERS_ENABLED = True
    RATELIMIT_DEFAULT = os.environ.get('RATE_LIMIT_DEFAULT', '200/day;50/hour')
    SWAGGER = {
        'title': 'HireSmart API',
        'uiversion': 3,
        'openapi': '3.0.2'
    }
    # Email
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True') == 'True'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = _fix_db_url(
        os.environ.get('DATABASE_URL', f'sqlite:///{base_dir / "hiresmart_dev.db"}')
    )


class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = _fix_db_url(
        os.environ.get('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/hiresmart')
    )


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = _fix_db_url(
        os.environ.get('DATABASE_URL', 'sqlite:///:memory:')
    )


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
