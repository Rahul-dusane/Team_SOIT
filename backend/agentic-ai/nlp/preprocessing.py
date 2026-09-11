"""
preprocessing.py
Pre-LLM NLP preprocessing utilities using spaCy, regex, and dateparser.
"""

import re
from typing import Dict, Any, Optional
import spacy
import dateparser
from datetime import datetime

# Email & Phone Regex Patterns
EMAIL_REGEX = re.compile(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+')
PHONE_REGEX = re.compile(r'\(?\+?[0-9]{1,4}\)?[-.\s]?[0-9]{1,4}[-.\s]?[0-9]{1,9}')

# Lazy spaCy model loading
_nlp = None

def get_spacy_nlp():
    global _nlp
    if _nlp is None:
        try:
            _nlp = spacy.load("en_core_web_sm")
        except Exception:
            _nlp = spacy.blank("en")
    return _nlp


def clean_text(text: str) -> str:
    """Clean and normalize raw text using spaCy lemmatization and whitespace normalization."""
    if not text or not text.strip():
        return ""
    
    nlp = get_spacy_nlp()
    doc = nlp(text)
    # Strip stop words, punctuation, and extra whitespace
    clean_tokens = [token.text for token in doc if not token.is_space and not token.is_punct]
    return " ".join(clean_tokens).strip()


def extract_contact_info(text: str) -> Dict[str, Optional[str]]:
    """Extract email and phone number using regex."""
    if not text:
        return {"email": None, "phone": None}
    emails = EMAIL_REGEX.findall(text)
    phones = PHONE_REGEX.findall(text)
    return {
        "email": emails[0] if emails else None,
        "phone": phones[0] if phones else None
    }


def parse_date_string(date_str: str) -> Optional[datetime]:
    """Parse ambiguous date string (e.g. 'Jan 2022', '03/2024', 'Present') to datetime."""
    if not date_str or str(date_str).lower() in ["present", "current", "now"]:
        return datetime.now()
    return dateparser.parse(str(date_str))


def calculate_experience_months(start_date_str: str, end_date_str: str = "Present") -> int:
    """Deterministic date math: returns duration in months between start and end dates."""
    start_dt = parse_date_string(start_date_str)
    end_dt = parse_date_string(end_date_str)
    if not start_dt or not end_dt or end_dt < start_dt:
        return 0
    return max(1, (end_dt.year - start_dt.year) * 12 + (end_dt.month - start_dt.month))
