"""
WSGI entry point for gunicorn.
Usage: gunicorn backend.wsgi:app  (from project root)
   or: gunicorn wsgi:app          (from backend/ directory)
"""
from app import create_app

app = create_app()
