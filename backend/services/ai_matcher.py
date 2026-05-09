import re
from typing import List, Tuple, Dict
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def normalize_terms(terms: List[str]) -> List[str]:
    return [re.sub(r'[^\w]+', ' ', term.lower()).strip() for term in terms if term]


def calculate_skill_match(candidate_skills: List[str], job_skills: List[str]) -> Tuple[List[str], List[str], float]:
    candidate_terms = [skill.lower() for skill in candidate_skills or []]
    job_terms = [skill.lower() for skill in job_skills or []]

    matched = []
    missing = []
    for job_skill in job_terms:
        if any(job_skill == candidate_skill or job_skill in candidate_skill or candidate_skill in job_skill for candidate_skill in candidate_terms):
            matched.append(job_skill.title())
        else:
            missing.append(job_skill.title())

    if not job_terms:
        score = 0.0
    else:
        score = round((len(matched) / len(job_terms)) * 100, 2)

    return matched, missing, score


def get_match_score(resume_text: str, candidate_skills: List[str], job_description: str, job_skills: List[str]) -> float:
    text_score = 0.0
    skill_score = 0.0

    if resume_text and job_description:
        vectorizer = TfidfVectorizer(stop_words='english')
        corpus = [resume_text, job_description]
        try:
            tfidf = vectorizer.fit_transform(corpus)
            similarity = cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0]
            text_score = round(similarity * 100, 2)
        except ValueError:
            text_score = 0.0

    _, _, skill_score = calculate_skill_match(candidate_skills, job_skills)

    if skill_score and text_score:
        final_score = round((skill_score * 0.7) + (text_score * 0.3), 2)
    else:
        final_score = round(max(skill_score, text_score), 2)

    return min(max(final_score, 0.0), 100.0)


def summarize_match(candidate_skills: List[str], job_skills: List[str]) -> Dict[str, object]:
    matched, missing, score = calculate_skill_match(candidate_skills, job_skills)
    return {
        'matched_skills': matched,
        'missing_skills': missing,
        'skill_score': score
    }
