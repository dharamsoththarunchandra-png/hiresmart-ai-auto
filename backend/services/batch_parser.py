import os
import zipfile
import tempfile
import stat
from werkzeug.utils import secure_filename
from services.resume_parser import extract_text_from_file, extract_skills_from_text

def remove_readonly(func, path, excinfo):
    """Callback for shutil.rmtree to handle readonly files."""
    os.chmod(path, stat.S_IWRITE)
    func(path)

def parse_batch_zip(zip_file_path: str):
    """
    Extracts a zip file to a temporary directory, parses all valid
    resumes inside, and returns a list of candidate summary data.
    """
    results = []
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Extract files
        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
            
        # Walk through the extracted files
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                ext = file.split('.')[-1].lower() if '.' in file else ''
                if ext in ['pdf', 'docx', 'doc']:
                    file_path = os.path.join(root, file)
                    original_name = file
                    try:
                        text = extract_text_from_file(file_path)
                        skills = extract_skills_from_text(text)
                        results.append({
                            'filename': original_name,
                            'status': 'success',
                            'skills': skills
                        })
                    except Exception as e:
                        results.append({
                            'filename': original_name,
                            'status': 'error',
                            'message': str(e)
                        })

    return results
