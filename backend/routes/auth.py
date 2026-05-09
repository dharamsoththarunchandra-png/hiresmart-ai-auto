from flask import Blueprint, request, current_app
from flask_jwt_extended import create_access_token
from flask_mail import Mail, Message
from database.db import db
from models import User, CandidateProfile, RecruiterProfile, Role
from utils.responses import success, error
import random, string, time

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# In-memory OTP store: { email: { otp, expires_at } }
_otp_store = {}


@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new candidate or recruiter."""
    payload = request.get_json() or {}
    email = payload.get('email', '').strip().lower()
    password = payload.get('password', '')
    first_name = payload.get('first_name', '').strip()
    last_name = payload.get('last_name', '').strip()
    role = payload.get('role', Role.CANDIDATE)

    if not email or not password or not first_name or not last_name:
        return error('Email, password, first name and last name are required', 400)

    if role not in (Role.CANDIDATE, Role.RECRUITER):
        return error('Role must be candidate or recruiter', 400)

    if User.query.filter_by(email=email).first():
        return error('Email already registered', 409)

    user = User(
        email=email,
        first_name=first_name,
        last_name=last_name,
        role=role
    )
    user.set_password(password)

    try:
        db.session.add(user)
        db.session.flush()

        if role == Role.RECRUITER:
            company_name = payload.get('company_name', '').strip()
            if not company_name:
                db.session.rollback()
                return error('Recruiter registration requires company_name', 400)

            recruiter_profile = RecruiterProfile(
                user_id=user.id,
                company_name=company_name,
                company_size=payload.get('company_size'),
                industry=payload.get('industry'),
                website=payload.get('website'),
                company_description=payload.get('company_description')
            )
            db.session.add(recruiter_profile)
        else:
            candidate_profile = CandidateProfile(
                user_id=user.id,
                title=payload.get('title'),
                bio=payload.get('bio'),
                location=payload.get('location'),
                years_of_experience=payload.get('years_of_experience', 0),
                skills=payload.get('skills', []),
                education=payload.get('education', []),
                certifications=payload.get('certifications', [])
            )
            db.session.add(candidate_profile)

        db.session.commit()

        access_token = create_access_token(identity=user.id, additional_claims={'role': user.role})
        return success({
            'user': user.to_dict(),
            'access_token': access_token
        }, 'Registration successful', 201)

    except Exception as exc:
        db.session.rollback()
        return error(str(exc), 500)


@auth_bp.route('/login', methods=['POST'])
def login():
    """Authenticate a user and issue a JWT token."""
    payload = request.get_json() or {}
    email = payload.get('email', '').strip().lower()
    password = payload.get('password', '')

    if not email or not password:
        return error('Email and password are required', 400)

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return error('Invalid credentials', 401)

    if not user.is_active:
        return error('Account is inactive', 403)

    access_token = create_access_token(identity=user.id, additional_claims={'role': user.role})
    return success({
        'user': user.to_dict(),
        'access_token': access_token
    }, 'Login successful', 200)


@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    """Send a 6-digit OTP to the user's email for password reset."""
    payload = request.get_json() or {}
    email = payload.get('email', '').strip().lower()

    if not email:
        return error('Email is required', 400)

    user = User.query.filter_by(email=email).first()
    if not user:
        # Return success anyway to avoid email enumeration
        return success({}, 'If that email exists, a reset code has been sent', 200)

    otp = ''.join(random.choices(string.digits, k=6))
    _otp_store[email] = {'otp': otp, 'expires_at': time.time() + 600}  # 10 min expiry

    try:
        from app import mail
        msg = Message(
            subject='HireSmart — Your Password Reset Code',
            recipients=[email],
            html=f"""
            <div style="font-family:Arial,sans-serif;max-width:480px;margin:0 auto;padding:32px;background:#f9fafb;border-radius:12px;">
                <h2 style="color:#1e1b4b;margin-bottom:8px;">Password Reset Code</h2>
                <p style="color:#6b7280;">Use the code below to reset your HireSmart password. It expires in <strong>10 minutes</strong>.</p>
                <div style="background:#fff;border:2px solid #e0e7ff;border-radius:10px;padding:24px;text-align:center;margin:24px 0;">
                    <span style="font-size:2.5rem;font-weight:800;letter-spacing:0.3em;color:#4f46e5;">{otp}</span>
                </div>
                <p style="color:#9ca3af;font-size:13px;">If you didn't request this, you can safely ignore this email.</p>
                <p style="color:#9ca3af;font-size:13px;">— The HireSmart Team</p>
            </div>
            """
        )
        mail.send(msg)
    except Exception as e:
        return error(f'Failed to send email: {str(e)}', 500)

    return success({}, 'Reset code sent to your email', 200)


@auth_bp.route('/verify-otp', methods=['POST'])
def verify_otp():
    """Verify the OTP sent to the user's email."""
    payload = request.get_json() or {}
    email = payload.get('email', '').strip().lower()
    otp = payload.get('otp', '').strip()

    if not email or not otp:
        return error('Email and OTP are required', 400)

    record = _otp_store.get(email)
    if not record:
        return error('No reset code found. Please request a new one.', 400)

    if time.time() > record['expires_at']:
        _otp_store.pop(email, None)
        return error('Reset code has expired. Please request a new one.', 400)

    if record['otp'] != otp:
        return error('Invalid reset code.', 400)

    return success({}, 'OTP verified', 200)


@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    """Reset the user's password after OTP verification."""
    payload = request.get_json() or {}
    email = payload.get('email', '').strip().lower()
    password = payload.get('password', '')

    if not email or not password:
        return error('Email and new password are required', 400)

    if email not in _otp_store:
        return error('OTP not verified. Please complete verification first.', 400)

    user = User.query.filter_by(email=email).first()
    if not user:
        return error('User not found', 404)

    user.set_password(password)
    db.session.commit()
    _otp_store.pop(email, None)

    return success({}, 'Password reset successfully', 200)
