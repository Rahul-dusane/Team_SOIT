"""
run_backend.py
One-click helper script to start the HireLens FastAPI Backend Server safely.
Sets single-threaded OpenBLAS environment variables to prevent Windows reloader crashes,
validates environment configuration, and launches uvicorn on port 8000.
"""

import os
import sys

# Standardize UTF-8 encoding for Windows terminals
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# 1. Prevent OpenBLAS memory allocation failures on Windows multi-threaded reloaders
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"

# 2. Add backend/agentic-ai directory to python path
backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend", "agentic-ai")
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

if __name__ == "__main__":
    import uvicorn
    print("=" * 65)
    print("Starting HireLens FastAPI Backend Server...")
    print("   Web API Base URL: http://localhost:8000/api/v1")
    print("   Interactive Docs: http://localhost:8000/docs")
    print("   Health Check:     http://localhost:8000/api/v1/health")
    use_reload = os.getenv("RELOAD", "false").lower() in ("true", "1")
    uvicorn.run("main:app", app_dir=backend_dir, host="0.0.0.0", port=8000, reload=use_reload)

