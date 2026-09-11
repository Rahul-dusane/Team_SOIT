"""Focused review: actual source functions, controlled NLP dependencies; NOT E2E.
Run with a Python environment containing Pydantic v2.
No network, model downloads, or changes to application code.
"""
import ast
import json
import pathlib
import re
import sys
import typing

ROOT = pathlib.Path(__file__).resolve().parents[1] / 'backend' / 'agentic-ai'
sys.path.insert(0, str(ROOT))
from contracts.candidate import CandidateProfile, CandidateSkill, CandidateExperience, CandidateProject
from contracts.job import JobProfile, JobRequirement
from contracts.match import FeatureBreakdown, ScoreBreakdown, RequirementAssessment, FailedRequirement
from config.matching_config import MatchingConfig, DEFAULT_MATCHING_CONFIG

ns = dict(vars(typing))
ns.update(globals())
ns['clean_text'] = lambda text: text
ns['semantic_similarity'] = lambda a, b: 0.0

def load(relative, names):
    tree = ast.parse((ROOT / relative).read_text(encoding='utf-8-sig'))
    nodes = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in names]
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(ROOT / relative), 'exec'), ns)

tree = ast.parse((ROOT / 'nlp/evidence_retriever.py').read_text())
neg = next(n for n in tree.body if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'NEGATION_REGEX' for t in n.targets))
exec(compile(ast.Module(body=[neg], type_ignores=[]), '<negation>', 'exec'), ns)
load('nlp/evidence_retriever.py', ['contains_negation', 'word_boundary_match', 'retrieve_candidate_evidence'])
load('matching/scorer.py', ['calculate_match_score'])
load('matching/rules.py', ['check_mandatory_requirements'])

results = []
def record(name, actual, expected):
    results.append(dict(name=name, actual=actual, expected=expected, passed=actual == expected))

def evidence(name, candidate, requirement, skill, expected, months=0):
    actual = ns['retrieve_candidate_evidence'](requirement, candidate, skill, months)[0]
    record(name, actual, expected)

def cand(**kw):
    return CandidateProfile(candidate_id='C', **kw)

evidence('Exact bookkeeping', cand(skills=[CandidateSkill(raw_skill='Bookkeeping')]), 'Bookkeeping', 'Bookkeeping', 'satisfied')
evidence('Java is not JavaScript', cand(skills=[CandidateSkill(raw_skill='Java')]), 'JavaScript', 'JavaScript', 'unknown')
evidence('Simple payroll negation', cand(experiences=[CandidateExperience(role='Accountant', description='I have no payroll experience')]), 'Payroll', 'Payroll', 'contradicted')
evidence('Empty candidate', cand(), 'Payroll', 'Payroll', 'unknown')
evidence('Generic word incorrectly satisfies certification', cand(skills=[CandidateSkill(raw_skill='Active listening')]), 'Active nursing license', 'Nursing license', 'unknown')
evidence('Unrelated contradiction contaminates payroll', cand(skills=[CandidateSkill(raw_skill='Python', evidence='No Python experience'), CandidateSkill(raw_skill='Payroll')]), 'Payroll', 'Payroll', 'satisfied')
evidence('Skill claim bypasses 60-month requirement', cand(skills=[CandidateSkill(raw_skill='Payroll')]), 'Payroll', 'Payroll', 'partially_supported', 60)
evidence('Two 12-month roles should meet 24 months', cand(experiences=[CandidateExperience(role='Accountant', description='Payroll', duration_months=12), CandidateExperience(role='Accountant', description='Payroll', duration_months=12)]), 'Payroll', 'Payroll', 'satisfied', 24)
evidence('C++ word boundary regression', cand(skills=[CandidateSkill(raw_skill='C++')]), 'C++', 'C++', 'satisfied')
evidence('No errors is not lack of experience', cand(experiences=[CandidateExperience(role='Accountant', description='Managed payroll with no errors')]), 'Payroll', 'Payroll', 'satisfied')
evidence('PII in returned evidence', cand(experiences=[CandidateExperience(role='Accountant', description='Payroll contact alice@example.test')]), 'Payroll', 'Payroll', 'satisfied')
ev = ns['retrieve_candidate_evidence']('Payroll', cand(experiences=[CandidateExperience(role='Accountant', description='Payroll contact alice@example.test')]), 'Payroll')[1]
record('Evidence output excludes email', 'alice@example.test' not in ev, True)
p = CandidateProfile.model_validate({'candidate_id':'C', 'portfolio_url':'example.test'})
record('Top-level unknown retained', p.unmapped_fields.get('portfolio_url'), 'example.test')
p = CandidateProfile.model_validate({'candidate_id':'C', 'experiences':[{'role':'Accountant','specialty':'Audit'}]})
record('Nested unknown retained', 'specialty' in p.experiences[0].model_dump(), True)
for name, assessments, expected in [
    ('Normal assessment score', [RequirementAssessment(requirement_id='R',description='Payroll',category='competency',weight=10,score_contribution=10)], 100.0),
    ('Zero weights must not imply perfect fit', [RequirementAssessment(requirement_id='R',description='Payroll',category='competency',weight=0,score_contribution=0)], 0.0),
]:
    score, breakdown = ns['calculate_match_score'](FeatureBreakdown(), assessments)
    record(name, score, expected)
    record(name + ' breakdown sums to score', round(sum(breakdown.model_dump().values()),2), score)
# No classifier dependency is reached when the explicit mandatory flag is ignored.
j = JobProfile(job_id='J',title='Nurse',requirements=[JobRequirement(description='Nursing license',category='certification',importance='preferred',mandatory=True)])
record('Explicit mandatory license enforced', ns['check_mandatory_requirements'](cand(),j)[0], False)
payload = dict(mode='isolated functions; real contracts; identity cleaner and zero semantic similarity; not full pipeline', results=results)
path = pathlib.Path(__file__).with_name('scenario_results.json')
path.write_text(json.dumps(payload,indent=2),encoding='utf-8')
for r in results:
    print(('PASS' if r['passed'] else 'FAIL'), r['name'], ':', r['actual'])
print(f"TOTAL {sum(r['passed'] for r in results)}/{len(results)} passed")
