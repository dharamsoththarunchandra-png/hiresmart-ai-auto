import os
import tempfile
from flask import Blueprint, request, current_app
from flask_jwt_extended import jwt_required
from werkzeug.utils import secure_filename
from utils.responses import success, error
from services.resume_parser import extract_text_from_file, extract_skills_from_text
from services.batch_parser import parse_batch_zip

upload_bp = Blueprint('upload', __name__, url_prefix='/upload')


def allowed_file(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions


@upload_bp.route('/resume', methods=['POST'])
@jwt_required()
def upload_resume():
    if 'file' not in request.files:
        return error('No file part', 400)
    file = request.files['file']
    if file.filename == '':
        return error('No selected file', 400)

    if file and allowed_file(file.filename, current_app.config['ALLOWED_EXTENSIONS']):
        filename = secure_filename(file.filename)
        # Use a temp directory so this works on read-only filesystems (e.g. Render)
        tmp_dir = tempfile.mkdtemp()
        filepath = os.path.join(tmp_dir, filename)
        file.save(filepath)

        try:
            text = extract_text_from_file(filepath)
            skills = extract_skills_from_text(text)
            return success({
                'filename': filename,
                'extracted_skills': skills
            }, 'Resume processed successfully')
        except Exception as e:
            return error(str(e), 500)
        finally:
            if os.path.exists(filepath):
                os.remove(filepath)
            os.rmdir(tmp_dir)

    return error('Invalid file type. Allowed: ' + ', '.join(current_app.config['ALLOWED_EXTENSIONS']), 400)


@upload_bp.route('/batch', methods=['POST'])
@jwt_required()
def upload_batch():
    if 'file' not in request.files:
        return error('No file part', 400)
    file = request.files['file']
    if file.filename == '':
        return error('No selected file', 400)

    if file and file.filename.lower().endswith(('.zip', '.tar', '.gz')):
        filename = secure_filename(file.filename)
        tmp_dir = tempfile.mkdtemp()
        filepath = os.path.join(tmp_dir, filename)
        file.save(filepath)

        try:
            results = parse_batch_zip(filepath)
            return success({
                'filename': filename,
                'total_processed': len(results),
                'results': results
            }, 'Batch processed successfully')
        except Exception as e:
            return error(str(e), 500)
        finally:
            if os.path.exists(filepath):
                os.remove(filepath)
            os.rmdir(tmp_dir)

    return error('Invalid file type. Only .zip archives are allowed for batch processing.', 400)
