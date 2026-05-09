from datetime import datetime
from database.db import db
from utils.security import hash_password, verify_password


class Role:
    CANDIDATE = 'candidate'
    RECRUITER = 'recruiter'
    ADMIN = 'admin'


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(30), nullable=False, default=Role.CANDIDATE)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    candidate_profile = db.relationship(
        'CandidateProfile', back_populates='user', uselist=False, cascade='all, delete-orphan'
    )
    recruiter_profile = db.relationship(
        'RecruiterProfile', back_populates='user', uselist=False, cascade='all, delete-orphan'
    )
    resumes = db.relationship('Resume', back_populates='user', cascade='all, delete-orphan')
    applications = db.relationship('Application', back_populates='candidate', cascade='all, delete-orphan')
    jobs = db.relationship('Job', back_populates='recruiter', cascade='all, delete-orphan')

    def set_password(self, password: str):
        self.password_hash = hash_password(password)

    def check_password(self, password: str) -> bool:
        return verify_password(password, self.password_hash)

    def get_full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class CandidateProfile(db.Model):
    __tablename__ = 'candidate_profiles'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    title = db.Column(db.String(150))
    bio = db.Column(db.Text)
    location = db.Column(db.String(200))
    years_of_experience = db.Column(db.Integer, default=0)
    skills = db.Column(db.JSON, default=list)
    education = db.Column(db.JSON, default=list)
    certifications = db.Column(db.JSON, default=list)
    github_url = db.Column(db.String(255))
    linkedin_url = db.Column(db.String(255))
    portfolio_url = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship('User', back_populates='candidate_profile')

    def to_dict(self):
        return {
            'title': self.title,
            'bio': self.bio,
            'location': self.location,
            'years_of_experience': self.years_of_experience,
            'skills': self.skills or [],
            'education': self.education or [],
            'certifications': self.certifications or [],
            'github_url': self.github_url,
            'linkedin_url': self.linkedin_url,
            'portfolio_url': self.portfolio_url,
        }


class RecruiterProfile(db.Model):
    __tablename__ = 'recruiter_profiles'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    company_name = db.Column(db.String(255), nullable=False)
    company_size = db.Column(db.String(100))
    industry = db.Column(db.String(150))
    website = db.Column(db.String(255))
    company_description = db.Column(db.Text)
    verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship('User', back_populates='recruiter_profile')

    def to_dict(self):
        return {
            'company_name': self.company_name,
            'company_size': self.company_size,
            'industry': self.industry,
            'website': self.website,
            'company_description': self.company_description,
            'verified': self.verified,
        }


class Job(db.Model):
    __tablename__ = 'jobs'

    id = db.Column(db.Integer, primary_key=True)
    recruiter_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    required_skills = db.Column(db.JSON, default=list)
    location = db.Column(db.String(255))
    salary_min = db.Column(db.Float)
    salary_max = db.Column(db.Float)
    experience_level = db.Column(db.String(100))
    employment_type = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, default=True)
    deadline = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    recruiter = db.relationship('User', back_populates='jobs')
    applications = db.relationship('Application', back_populates='job', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'required_skills': self.required_skills or [],
            'location': self.location,
            'salary_min': self.salary_min,
            'salary_max': self.salary_max,
            'experience_level': self.experience_level,
            'employment_type': self.employment_type,
            'is_active': self.is_active,
            'deadline': self.deadline.isoformat() if self.deadline else None,
            'recruiter_id': self.recruiter_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class Resume(db.Model):
    __tablename__ = 'resumes'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_size = db.Column(db.Integer)
    extracted_text = db.Column(db.Text)
    extracted_skills = db.Column(db.JSON, default=list)
    is_primary = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship('User', back_populates='resumes')
    applications = db.relationship('Application', back_populates='resume')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'original_filename': self.original_filename,
            'file_size': self.file_size,
            'extracted_skills': self.extracted_skills or [],
            'is_primary': self.is_primary,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class Application(db.Model):
    __tablename__ = 'applications'

    id = db.Column(db.Integer, primary_key=True)
    candidate_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id'), nullable=False)
    resume_id = db.Column(db.Integer, db.ForeignKey('resumes.id'))
    status = db.Column(db.String(50), default='applied')
    match_score = db.Column(db.Float)
    cover_letter = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    candidate = db.relationship('User', back_populates='applications')
    job = db.relationship('Job', back_populates='applications')
    resume = db.relationship('Resume', back_populates='applications')

    def to_dict(self):
        return {
            'id': self.id,
            'candidate_id': self.candidate_id,
            'job_id': self.job_id,
            'resume_id': self.resume_id,
            'status': self.status,
            'match_score': self.match_score,
            'cover_letter': self.cover_letter,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
