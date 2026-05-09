import bcrypt
from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity


def hash_password(password: str) -> str:
    """Hash a plaintext password using bcrypt."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')


def verify_password(password: str, hashed: str) -> bool:
    """Verify a plaintext password against a bcrypt hash."""
    try:
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    except ValueError:
        return False


def role_required(*allowed_roles):
    """Protect endpoints so only allowed roles can access them."""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            identity = get_jwt_identity()
            from models import User
            user = User.query.get(identity)
            if not user or user.role not in allowed_roles:
                return jsonify({'error': 'Forbidden'}), 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator
