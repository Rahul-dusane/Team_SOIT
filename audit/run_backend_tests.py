"""Run backend tests without using project credentials or production data."""
import os
import pathlib
import sys
import uuid

ROOT = pathlib.Path(__file__).resolve().parents[1]
BACKEND = ROOT / 'backend' / 'agentic-ai'
db_path = ROOT / 'audit' / ('test_' + uuid.uuid4().hex + '.db')
os.environ.update({
    'PYTHON_DOTENV_DISABLED': '1', 'TESTING': 'false',
    'DATABASE_URL': 'sqlite:///' + db_path.as_posix(),
    'SUPABASE_DB_URL': '', 'OPENAI_API_KEY': '', 'GEMINI_API_KEY': '',
    'GOOGLE_API_KEY': '', 'LLM_PROVIDER': 'mock', 'LANGSMITH_TRACING': 'false',
    'LANGCHAIN_TRACING_V2': 'false', 'HF_HUB_OFFLINE': '1',
    'TRANSFORMERS_OFFLINE': '1', 'OPENBLAS_NUM_THREADS': '1', 'OMP_NUM_THREADS': '1',
})
sys.path.insert(0, str(BACKEND))
if __name__ == '__main__':
    import pytest
    print('Isolated SQLite:', db_path)
    print('LLM credentials disabled; embedding fallback used if model unavailable.')
    sys.exit(pytest.main([str(BACKEND / 'tests'), '-q', '-p', 'no:cacheprovider',
        '--tb=short', '--junitxml=' + str(ROOT / 'audit' / 'backend_tests.xml')]))
