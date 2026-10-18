"""Vercel entrypoint for the LearnLens FastAPI service.

In Vercel, set this project's Root Directory to `backend`. The Python runtime
recognizes `index.py` and serves the exported ASGI `app`.
"""
from app.main import app

__all__ = ["app"]
