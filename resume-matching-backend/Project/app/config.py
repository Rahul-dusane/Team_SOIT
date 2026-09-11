"""
Central configuration: known skills vocabulary, education level ranks,
and the weights used when combining individual matcher scores into a
single overall match score.
"""

# A reasonably broad, extensible vocabulary of skills the extractor looks for.
# In production this would likely be backed by a database or an external
# taxonomy (e.g. ESCO, LinkedIn Skills API), but a static list keeps this
# backend self-contained and dependency-free.
KNOWN_SKILLS = {
    "python", "java", "javascript", "typescript", "c++", "c#", "go", "rust",
    "sql", "nosql", "mongodb", "postgresql", "mysql", "redis",
    "django", "flask", "fastapi", "spring", "react", "angular", "vue",
    "node.js", "express", "html", "css", "tailwind",
    "aws", "azure", "gcp", "docker", "kubernetes", "terraform", "ci/cd",
    "git", "linux", "bash", "shell scripting",
    "machine learning", "deep learning", "nlp", "computer vision",
    "pandas", "numpy", "scikit-learn", "tensorflow", "pytorch",
    "data analysis", "data engineering", "etl", "spark", "hadoop",
    "rest api", "graphql", "microservices", "agile", "scrum",
    "project management", "communication", "leadership", "problem solving",
}

# Education levels ranked lowest to highest.
EDUCATION_RANKS = {
    "high school": 1,
    "diploma": 2,
    "associate": 2,
    "bachelor": 3,
    "b.tech": 3,
    "b.sc": 3,
    "be": 3,
    "master": 4,
    "m.tech": 4,
    "m.sc": 4,
    "mba": 4,
    "phd": 5,
    "doctorate": 5,
}

# Weights for the overall aggregated score. Must sum to 1.0.
MATCH_WEIGHTS = {
    "skills": 0.45,
    "experience": 0.20,
    "education": 0.15,
    "role": 0.20,
}
