import os
import shutil
import tempfile
from flask import Blueprint, request
from services.resume_parser import extract_text_from_file, extract_skills_from_text, safe_filename
from services.ai_matcher import get_match_score, summarize_match
from utils.responses import success, error

analyze_bp = Blueprint('analyze', __name__, url_prefix='/analyze')


@analyze_bp.route('/screen', methods=['POST'])
def screen_resumes():
    """
    Accept one or more resume files + a job description,
    extract text via NLP, compute TF-IDF cosine similarity score,
    and return ranked results.
    """
    job_description = request.form.get('job_description', '').strip()
    if not job_description:
        return error('Job description is required', 400)

    files = request.files.getlist('resumes')
    if not files or all(f.filename == '' for f in files):
        return error('At least one resume file is required', 400)

    results = []
    tmp_dir = tempfile.mkdtemp()

    try:
        for f in files:
            if not f.filename:
                continue

            ext = os.path.splitext(f.filename)[1].lower()
            if ext not in ('.pdf', '.doc', '.docx'):
                results.append({
                    'filename': f.filename,
                    'error': 'Unsupported file type. Use PDF or DOCX.'
                })
                continue

            safe_name = safe_filename(f.filename)
            tmp_path = os.path.join(tmp_dir, safe_name)
            f.save(tmp_path)

            try:
                resume_text = extract_text_from_file(tmp_path)
                if not resume_text.strip():
                    results.append({'filename': f.filename, 'error': 'Could not extract text from file.'})
                    continue

                candidate_skills = extract_skills_from_text(resume_text)
                job_skills = extract_skills_from_text(job_description)

                match_score = get_match_score(resume_text, candidate_skills, job_description, job_skills)
                summary = summarize_match(candidate_skills, job_skills)

                # Classification
                if match_score >= 70:
                    classification = 'Qualified'
                elif match_score >= 40:
                    classification = 'Partially Qualified'
                else:
                    classification = 'Not Qualified'

                results.append({
                    'filename': f.filename,
                    'match_score': round(match_score, 1),
                    'classification': classification,
                    'candidate_skills': candidate_skills,
                    'matched_skills': summary['matched_skills'],
                    'missing_skills': summary['missing_skills'],
                    'skill_score': summary['skill_score'],
                    'resume_preview': resume_text[:300] + '...' if len(resume_text) > 300 else resume_text
                })

            except Exception as e:
                results.append({'filename': f.filename, 'error': str(e)})
            finally:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)

    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)

    # Sort by match_score descending
    results.sort(key=lambda x: x.get('match_score', -1), reverse=True)

    qualified = [r for r in results if r.get('classification') == 'Qualified']
    partial = [r for r in results if r.get('classification') == 'Partially Qualified']
    not_qualified = [r for r in results if r.get('classification') == 'Not Qualified']

    return success({
        'total': len(results),
        'qualified_count': len(qualified),
        'partial_count': len(partial),
        'not_qualified_count': len(not_qualified),
        'results': results
    }, 'Screening complete', 200)
