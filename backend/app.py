import os
from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flasgger import Swagger
from flask_jwt_extended import JWTManager
from flask_mail import Mail

mail = Mail()

from config import config
from database.db import db
from routes.auth import auth_bp
from routes.users import user_bp
from routes.jobs import job_bp
from routes.applications import applications_bp
from routes.upload import upload_bp
from routes.analyze import analyze_bp


def create_app(config_name=None):
    """Application factory."""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Initialize extensions
    CORS(app)
    db.init_app(app)
    jwt = JWTManager(app)
    mail.init_app(app)

    # Rate limiting
    limiter = Limiter(
        get_remote_address,
        app=app,
        default_limits=[app.config['RATELIMIT_DEFAULT']]
    )

    # Swagger documentation
    Swagger(app)

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(job_bp)
    app.register_blueprint(applications_bp)
    app.register_blueprint(upload_bp)
    app.register_blueprint(analyze_bp)

    # Serve frontend static files
    frontend_dir = os.path.join(os.path.dirname(__file__), '..', 'frontend')

    @app.route('/')
    def index():
        return send_from_directory(frontend_dir, 'index.html')

    @app.route('/<path:filename>')
    def static_files(filename):
        return send_from_directory(frontend_dir, filename)

    # Create database tables
    with app.app_context():
        db.create_all()

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=app.config['DEBUG'], host='0.0.0.0', port=5000)