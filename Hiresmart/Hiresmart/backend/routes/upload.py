import os
from flask import Blueprint, request, current_app
from werkzeug.utils import secure_filename
from utils.responses import success, error
from services.resume_parser import extract_text_from_file, extract_skills_from_text
from services.batch_parser import parse_batch_zip

upload_bp = Blueprint('upload', __name__, url_prefix='/upload')

def allowed_file(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

@upload_bp.route('/resume', methods=['POST'])
def upload_resume():
    if 'file' not in request.files:
        return error('No file part', 400)
    file = request.files['file']
    if file.filename == '':
        return error('No selected file', 400)
    
    if file and allowed_file(file.filename, current_app.config['ALLOWED_EXTENSIONS']):
        filename = secure_filename(file.filename)
        os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
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
    return error('Invalid file type. Allowed extensions: ' + ', '.join(current_app.config['ALLOWED_EXTENSIONS']), 400)

@upload_bp.route('/batch', methods=['POST'])
def upload_batch():
    if 'file' not in request.files:
        return error('No file part', 400)
    file = request.files['file']
    if file.filename == '':
        return error('No selected file', 400)
        
    if file and file.filename.lower().endswith(('.zip', '.tar', '.gz')):
        filename = secure_filename(file.filename)
        os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
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
    return error('Invalid file type. Only archive formats like .zip are allowed for batch processing.', 400)
