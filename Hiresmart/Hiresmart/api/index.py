"""
Vercel serverless entry point.
This wraps the Flask app for Vercel's serverless environment.
"""
import sys
import os

# Add backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app import create_app

app = create_app('production')

# Vercel expects the WSGI app to be named 'app'
# This is the handler for all requests
