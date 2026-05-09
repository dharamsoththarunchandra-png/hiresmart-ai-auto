from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from database.db import db
from models import User, Job, Role
from utils.responses import success, error
from utils.security import role_required
from datetime import datetime

job_bp = Blueprint('jobs', __name__, url_prefix='/jobs')


def _build_job_payload(job):
    return {
        'id': job.id,
        'title': job.title,
        'description': job.description,
        'required_skills': job.required_skills or [],
        'location': job.location,
        'salary_min': job.salary_min,
        'salary_max': job.salary_max,
        'experience_level': job.experience_level,
        'employment_type': job.employment_type,
        'is_active': job.is_active,
        'deadline': job.deadline.isoformat() if job.deadline else None,
        'recruiter_id': job.recruiter_id,
        'created_at': job.created_at.isoformat() if job.created_at else None,
        'updated_at': job.updated_at.isoformat() if job.updated_at else None,
    }


@job_bp.route('', methods=['GET'])
def list_jobs():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    location = request.args.get('location', '').strip().lower()
    skills = [item.strip().lower() for item in request.args.get('skills', '').split(',') if item.strip()]

    query = Job.query.filter_by(is_active=True).order_by(Job.created_at.desc()).all()
    filtered = []

    for job in query:
        if location and job.location and location not in job.location.lower():
            continue
        if skills:
            raw_skills = [s.lower() for s in (job.required_skills or [])]
            if not all(skill in raw_skills for skill in skills):
                continue
        filtered.append(job)

    total = len(filtered)
    start = (page - 1) * per_page
    end = start + per_page
    items = filtered[start:end]

    return success({
        'jobs': [_build_job_payload(job) for job in items],
        'total': total,
        'page': page,
        'per_page': per_page
    })


@job_bp.route('', methods=['POST'])
@jwt_required()
@role_required(Role.RECRUITER)
def create_job():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user or user.role != Role.RECRUITER:
        return error('Only recruiters can create jobs', 403)

    payload = request.get_json() or {}
    title = payload.get('title', '').strip()
    description = payload.get('description', '').strip()
    if not title or not description:
        return error('Job title and description are required', 400)

    deadline = None
    if payload.get('deadline'):
        try:
            deadline = datetime.fromisoformat(payload['deadline'])
        except ValueError:
            return error('Invalid deadline format. Use ISO 8601.', 400)

    job = Job(
        recruiter_id=user.id,
        title=title,
        description=description,
        required_skills=payload.get('required_skills', []),
        location=payload.get('location'),
        salary_min=payload.get('salary_min'),
        salary_max=payload.get('salary_max'),
        experience_level=payload.get('experience_level'),
        employment_type=payload.get('employment_type'),
        deadline=deadline
    )

    try:
        db.session.add(job)
        db.session.commit()
        return success(_build_job_payload(job), 'Job created successfully', 201)
    except Exception as exc:
        db.session.rollback()
        return error(str(exc), 500)


@job_bp.route('/<int:job_id>', methods=['GET'])
def get_job(job_id):
    job = Job.query.get(job_id)
    if not job:
        return error('Job not found', 404)

    payload = _build_job_payload(job)
    payload['recruiter'] = {
        'id': job.recruiter.id,
        'email': job.recruiter.email,
        'name': job.recruiter.get_full_name()
    }
    payload['applicants_count'] = len(job.applications)
    return success(payload)


@job_bp.route('/<int:job_id>', methods=['PUT'])
@jwt_required()
@role_required(Role.RECRUITER)
def update_job(job_id):
    user_id = get_jwt_identity()
    job = Job.query.get(job_id)
    if not job:
        return error('Job not found', 404)
    if job.recruiter_id != user_id:
        return error('Unauthorized', 403)

    payload = request.get_json() or {}
    job.title = payload.get('title', job.title)
    job.description = payload.get('description', job.description)
    job.required_skills = payload.get('required_skills', job.required_skills)
    job.location = payload.get('location', job.location)
    job.salary_min = payload.get('salary_min', job.salary_min)
    job.salary_max = payload.get('salary_max', job.salary_max)
    job.experience_level = payload.get('experience_level', job.experience_level)
    job.employment_type = payload.get('employment_type', job.employment_type)
    try:
        if payload.get('deadline'):
            job.deadline = datetime.fromisoformat(payload['deadline'])
    except ValueError:
        return error('Invalid deadline format. Use ISO 8601.', 400)

    try:
        db.session.commit()
        return success(_build_job_payload(job), 'Job updated successfully')
    except Exception as exc:
        db.session.rollback()
        return error(str(exc), 500)


@job_bp.route('/<int:job_id>', methods=['DELETE'])
@jwt_required()
@role_required(Role.RECRUITER)
def delete_job(job_id):
    user_id = get_jwt_identity()
    job = Job.query.get(job_id)
    if not job:
        return error('Job not found', 404)
    if job.recruiter_id != user_id:
        return error('Unauthorized', 403)

    try:
        db.session.delete(job)
        db.session.commit()
        return success(message='Job deleted successfully')
    except Exception as exc:
        db.session.rollback()
        return error(str(exc), 500)


@job_bp.route('/<int:job_id>/applicants', methods=['GET'])
@jwt_required()
@role_required(Role.RECRUITER)
def get_job_applicants(job_id):
    user_id = get_jwt_identity()
    job = Job.query.get(job_id)
    if not job:
        return error('Job not found', 404)
    if job.recruiter_id != user_id:
        return error('Unauthorized', 403)

    applicants = [
        {
            'application_id': application.id,
            'candidate_id': application.candidate_id,
            'candidate_name': application.candidate.get_full_name(),
            'candidate_email': application.candidate.email,
            'status': application.status,
            'match_score': application.match_score,
            'applied_at': application.created_at.isoformat() if application.created_at else None
        }
        for application in job.applications
    ]

    return success({
        'job_id': job.id,
        'job_title': job.title,
        'applicants': applicants
    })
