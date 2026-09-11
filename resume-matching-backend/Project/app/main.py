"""
Entrypoint used to run the app with:
    uvicorn app.main:app --reload
"""

from app import create_app

app = create_app()
