import os
import re
from typing import List
from PyPDF2 import PdfReader
from docx import Document

SUPPORTED_EXTENSIONS = {'pdf', 'docx'}


def extract_text_from_pdf(file_path: str) -> str:
    text = []
    with open(file_path, 'rb') as fh:
        reader = PdfReader(fh)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text.append(page_text)
    return '\n'.join(text).strip()


def extract_text_from_docx(file_path: str) -> str:
    document = Document(file_path)
    lines = [paragraph.text for paragraph in document.paragraphs if paragraph.text]
    return '\n'.join(lines).strip()


def extract_text_from_file(file_path: str) -> str:
    extension = os.path.splitext(file_path)[1].lower().strip('.')
    if extension == 'pdf':
        return extract_text_from_pdf(file_path)
    if extension == 'docx':
        return extract_text_from_docx(file_path)
    raise ValueError('Unsupported file type. Only PDF and DOCX are accepted.')


def normalize_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s\-\.]+', ' ', text)
    return re.sub(r'\s+', ' ', text).strip()


def extract_skills_from_text(text: str) -> List[str]:
    text_lower = normalize_text(text)
    SKILL_KEYWORDS = {
        'python', 'java', 'javascript', 'typescript', 'csharp', 'c++', 'c', 'go', 'rust',
        'php', 'ruby', 'swift', 'kotlin', 'scala', 'r', 'matlab', 'sql', 'html', 'css',
        'django', 'flask', 'fastapi', 'react', 'angular', 'vue', 'node', 'express',
        'spring', 'asp.net', 'laravel', 'rails', 'next', 'nuxt',
        'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch', 'cassandra',
        'dynamodb', 'oracle', 'sqlite', 'firebase', 'git', 'docker', 'kubernetes',
        'jenkins', 'aws', 'azure', 'gcp', 'pandas', 'numpy', 'scikit-learn', 'tensorflow',
        'pytorch', 'keras', 'pandas', 'numpy', 'hadoop', 'spark', 'tableau', 'powerbi',
        'linux', 'bash', 'rest', 'graphql', 'api', 'nlp', 'machine learning', 'deep learning'
    }

    found = set()
    for skill in SKILL_KEYWORDS:
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, text_lower):
            found.add(skill.title())

    return sorted(found)


def safe_filename(filename: str) -> str:
    return re.sub(r'[^a-zA-Z0-9_.-]', '_', filename)
