from app.matching.skill_matcher import match_skills
from app.matching.experience_matcher import match_experience
from app.matching.education_matcher import match_education
from app.matching.role_matcher import match_role
from app.matching.aggregator import compute_overall_match


RESUME = """
Senior Software Engineer with 5 years of experience building backend
systems in Python, Django, and PostgreSQL. Holds a Bachelor degree in
Computer Science. Experienced with Docker, AWS, and REST APIs.
"""

JOB = """
We are hiring a Software Engineer with at least 3 years of experience.
Required skills: Python, Django, PostgreSQL, Docker. Bachelor degree
required.
"""


def test_match_skills_finds_overlap():
    result = match_skills(RESUME, JOB)
    assert "python" in result["matched_skills"]
    assert "django" in result["matched_skills"]
    assert result["score"] == 1.0  # resume covers all required job skills


def test_match_skills_flags_missing():
    result = match_skills("Python developer.", "Requires Python and Kubernetes.")
    assert "kubernetes" in result["missing_skills"]
    assert result["score"] == 0.5


def test_match_experience_meets_requirement():
    result = match_experience(RESUME, JOB)
    assert result["resume_years"] == 5.0
    assert result["required_years"] == 3.0
    assert result["score"] == 1.0


def test_match_experience_falls_short():
    result = match_experience("1 year of experience.", "Requires 4 years experience.")
    assert result["score"] == 0.25


def test_match_education_meets_requirement():
    result = match_education(RESUME, JOB)
    assert result["resume_level"] == "bachelor"
    assert result["score"] == 1.0


def test_match_education_falls_short():
    result = match_education("High school diploma.", "Requires a Master degree.")
    assert result["score"] < 1.0


def test_match_role_with_explicit_title():
    result = match_role(RESUME, JOB, job_title="Software Engineer")
    assert result["score"] > 0.0


def test_compute_overall_match_shape():
    result = compute_overall_match(RESUME, JOB, job_title="Software Engineer")
    assert 0.0 <= result["overall_score"] <= 1.0
    assert set(result.keys()) == {
        "overall_score", "skills", "experience", "education", "role"
    }
