from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from database.db import db
from models import User, Job, Resume, Application, Role
from services.ai_matcher import get_match_score
from utils.responses import success, error
from utils.security import role_required

applications_bp = Blueprint('applications', __name__)


@applications_bp.route('/apply', methods=['POST'])
@jwt_required()
@role_required(Role.CANDIDATE)
def apply_to_job():
    payload = request.get_json() or {}
    job_id = payload.get('job_id')
    resume_id = payload.get('resume_id')
    cover_letter = payload.get('cover_letter')

    if not job_id:
        return error('job_id is required', 400)

    user_id = get_jwt_identity()
    job = Job.query.get(job_id)
    if not job or not job.is_active:
        return error('Job not found', 404)

    if Application.query.filter_by(job_id=job_id, candidate_id=user_id).first():
        return error('You already applied to this job', 400)

    resume = None
    if resume_id:
        resume = Resume.query.get(resume_id)
        if not resume or resume.user_id != user_id:
            return error('Resume not found', 404)
    else:
        resume = Resume.query.filter_by(user_id=user_id, is_primary=True).first()
        if not resume:
            return error('No primary resume found. Upload a resume first.', 400)

    match_score = get_match_score(
        resume.extracted_text or '',
        resume.extracted_skills or [],
        job.description or '',
        job.required_skills or []
    )

    application = Application(
        candidate_id=user_id,
        job_id=job_id,
        resume_id=resume.id,
        status='applied',
        match_score=match_score,
        cover_letter=cover_letter
    )

    try:
        db.session.add(application)
        db.session.commit()
        return success({
            'application_id': application.id,
            'job_id': job.id,
            'status': application.status,
            'match_score': application.match_score
        }, 'Application submitted successfully', 201)
    except Exception as exc:
        db.session.rollback()
        return error(str(exc), 500)


@applications_bp.route('/applications', methods=['GET'])
@jwt_required()
def list_applications():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return error('User not found', 404)

    if user.role == Role.CANDIDATE:
        applications = Application.query.filter_by(candidate_id=user_id).all()
    else:
        jobs = Job.query.filter_by(recruiter_id=user_id).all()
        job_ids = [job.id for job in jobs]
        applications = Application.query.filter(Application.job_id.in_(job_ids)).all()

    data = [
        {
            'id': app.id,
            'job_id': app.job_id,
            'job_title': app.job.title,
            'candidate_id': app.candidate_id,
            'candidate_name': app.candidate.get_full_name(),
            'status': app.status,
            'match_score': app.match_score,
            'applied_at': app.created_at.isoformat() if app.created_at else None
        }
        for app in applications
    ]

    return success({'applications': data})


@applications_bp.route('/applications/<int:application_id>/status', methods=['PUT'])
@jwt_required()
@role_required(Role.RECRUITER)
def update_application_status(application_id):
    payload = request.get_json() or {}
    new_status = payload.get('status', '').strip().lower()
    if new_status not in {'applied', 'reviewed', 'shortlisted', 'rejected'}:
        return error('Invalid status value', 400)

    application = Application.query.get(application_id)
    if not application:
        return error('Application not found', 404)

    recruiter_id = get_jwt_identity()
    if application.job.recruiter_id != recruiter_id:
        return error('Unauthorized', 403)

    application.status = new_status
    try:
        db.session.commit()
        return success(application.to_dict(), 'Application status updated successfully')
    except Exception as exc:
        db.session.rollback()
        return error(str(exc), 500)
