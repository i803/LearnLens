from __future__ import annotations
import os
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "").strip()
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "openrouter/free").strip()
OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1").strip().rstrip("/")
OPENROUTER_SITE_URL = os.getenv("OPENROUTER_SITE_URL", "http://localhost:3000").strip()
OPENROUTER_APP_NAME = os.getenv("OPENROUTER_APP_NAME", "LearnLens AI").strip()
OPENROUTER_TIMEOUT_SECONDS = float(os.getenv("OPENROUTER_TIMEOUT_SECONDS", "25"))
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash").strip()
GEMINI_BASE_URL = os.getenv("GEMINI_BASE_URL", "https://generativelanguage.googleapis.com/v1beta").strip().rstrip("/")
SUPABASE_URL = os.getenv("SUPABASE_URL", "").strip().rstrip("/")
SUPABASE_SECRET_KEY = os.getenv("SUPABASE_SECRET_KEY", "").strip()
AI_ENABLED = os.getenv("AI_ENABLED", "true").lower() == "true"
DEMO_MODE = os.getenv("DEMO_MODE", "false").lower() == "true"
RAG_ENABLED = os.getenv("RAG_ENABLED", "true").lower() == "true"
DEMO_TIME_TRAVEL = os.getenv("DEMO_TIME_TRAVEL", "false").lower() == "true"
MAX_UPLOAD_MB = float(os.getenv("MAX_UPLOAD_MB", "8"))
RATE_LIMIT_PER_MIN = int(os.getenv("RATE_LIMIT_PER_MIN", "300"))
RATE_LIMIT_HEAVY_PER_MIN = int(os.getenv("RATE_LIMIT_HEAVY_PER_MIN", "40"))
FRONTEND_ORIGINS = [x.strip().rstrip("/") for x in os.getenv("FRONTEND_ORIGINS", os.getenv("FRONTEND_ORIGIN", "http://localhost:3000")).split(",") if x.strip()]
FRONTEND_ORIGIN = FRONTEND_ORIGINS[0] if FRONTEND_ORIGINS else "http://localhost:3000"

def openrouter_configured() -> bool:
    return AI_ENABLED and not DEMO_MODE and bool(OPENROUTER_API_KEY) and (
        OPENROUTER_MODEL == "openrouter/free" or OPENROUTER_MODEL.endswith(":free")
    )

def gemini_configured() -> bool:
    # The model name is explicitly configurable; use only free-tier-eligible models/accounts.
    return AI_ENABLED and not DEMO_MODE and bool(GEMINI_API_KEY) and GEMINI_MODEL.startswith("gemini-")

def ai_configured() -> bool:
    return openrouter_configured() or gemini_configured()

def supabase_configured() -> bool:
    return bool(SUPABASE_URL and SUPABASE_SECRET_KEY)
