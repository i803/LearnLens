from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[2]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))


import pytest

@pytest.fixture(autouse=True)
def _reset_rate_limit(monkeypatch):
    from app import main
    from app.persistence import persistence
    main._hits.clear()
    # Tests use isolated in-memory fixtures and must never write to a developer's
    # configured Supabase project merely because backend/.env exists locally.
    monkeypatch.setattr(persistence.db, "enabled", False)
    yield
