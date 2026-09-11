# nlp package initialization
from .aliases import lookup_alias
from .preprocessing import clean_text, extract_contact_info, calculate_experience_months
from .skill_normalizer import normalize_skill
from .skill_relationships import get_skill_relationship, get_transferability_score
from .role_normalizer import normalize_role
from .embeddings import embed_text, embed_skills, EmbeddingService
from .similarity import semantic_similarity
