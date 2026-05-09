from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from database.db import db
from models import User, CandidateProfile, RecruiterProfile, Role
from utils.responses import success, error

user_bp = Blueprint('user', __name__, url_prefix='/user')


@user_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return error('User not found', 404)

    profile = user.to_dict()
    if user.role == Role.CANDIDATE and user.candidate_profile:
        profile['candidate_profile'] = user.candidate_profile.to_dict()
    if user.role == Role.RECRUITER and user.recruiter_profile:
        profile['recruiter_profile'] = user.recruiter_profile.to_dict()

    return success(profile)


@user_bp.route('/profile/candidate', methods=['PUT'])
@jwt_required()
def update_candidate_profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user or user.role != Role.CANDIDATE:
        return error('Only candidates may update this profile', 403)

    payload = request.get_json() or {}
    profile = user.candidate_profile
    if not profile:
        profile = CandidateProfile(user_id=user_id)
        db.session.add(profile)

    profile.title = payload.get('title', profile.title)
    profile.bio = payload.get('bio', profile.bio)
    profile.location = payload.get('location', profile.location)
    profile.years_of_experience = payload.get('years_of_experience', profile.years_of_experience)
    profile.skills = payload.get('skills', profile.skills or [])
    profile.education = payload.get('education', profile.education or [])
    profile.certifications = payload.get('certifications', profile.certifications or [])
    profile.github_url = payload.get('github_url', profile.github_url)
    profile.linkedin_url = payload.get('linkedin_url', profile.linkedin_url)
    profile.portfolio_url = payload.get('portfolio_url', profile.portfolio_url)

    try:
        db.session.commit()
        return success(profile.to_dict(), 'Candidate profile updated successfully')
    except Exception as exc:
        db.session.rollback()
        return error(str(exc), 500)


@user_bp.route('/profile/recruiter', methods=['PUT'])
@jwt_required()
def update_recruiter_profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user or user.role != Role.RECRUITER:
        return error('Only recruiters may update this profile', 403)

    payload = request.get_json() or {}
    profile = user.recruiter_profile
    if not profile:
        profile = RecruiterProfile(user_id=user_id, company_name=payload.get('company_name', ''))
        db.session.add(profile)

    profile.company_name = payload.get('company_name', profile.company_name)
    profile.company_size = payload.get('company_size', profile.company_size)
    profile.industry = payload.get('industry', profile.industry)
    profile.website = payload.get('website', profile.website)
    profile.company_description = payload.get('company_description', profile.company_description)

    try:
        db.session.commit()
        return success(profile.to_dict(), 'Recruiter profile updated successfully')
    except Exception as exc:
        db.session.rollback()
        return error(str(exc), 500)


@user_bp.route('/<int:user_id>', methods=['GET'])
def get_public_profile(user_id):
    user = User.query.get(user_id)
    if not user:
        return error('User not found', 404)

    profile = {
        'id': user.id,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'role': user.role,
        'full_name': user.get_full_name()
    }

    if user.role == Role.CANDIDATE and user.candidate_profile:
        profile['candidate_profile'] = {
            'title': user.candidate_profile.title,
            'location': user.candidate_profile.location,
            'years_of_experience': user.candidate_profile.years_of_experience,
            'skills': user.candidate_profile.skills or []
        }
    if user.role == Role.RECRUITER and user.recruiter_profile:
        profile['recruiter_profile'] = {
            'company_name': user.recruiter_profile.company_name,
            'industry': user.recruiter_profile.industry,
        }

    return success(profile)
