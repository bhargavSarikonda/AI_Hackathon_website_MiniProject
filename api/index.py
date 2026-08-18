"""
Vercel Serverless Function Entrypoint
Bridges Vercel Serverless Python Runtime to FastAPI backend.
"""

import sys
from pathlib import Path

# Add backend directory to Python system path
ROOT_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = ROOT_DIR / "backend"

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from main import app  # ASGI app instance for Vercel
