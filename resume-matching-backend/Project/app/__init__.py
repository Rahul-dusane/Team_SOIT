"""
app package
Resume <-> Job Description Matching Backend

Exposes create_app(), a FastAPI application factory.
"""

def create_app():
    """
    Builds and returns the FastAPI application. Imports are deferred to
    inside this function so that `app.matching` / `app.preprocessing`
    (pure Python, no web framework dependency) can be imported and unit
    tested even in environments without FastAPI installed.
    """
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware

    app = FastAPI(
        title="Resume Matching API",
        description="Matches resumes against job descriptions using skill, "
                     "experience, education, and role matchers.",
        version="1.0.0",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Import here to avoid circular imports at module load time
    from app.routes import router

    app.include_router(router)

    return app
