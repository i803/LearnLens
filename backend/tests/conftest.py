from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[2]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))
<<<<<<< HEAD


import pytest

@pytest.fixture(autouse=True)
def _reset_rate_limit():
    from app import main
    main._hits.clear()
    yield
=======
>>>>>>> b9d02d34e42932237d9f91969848006efc59b2b1
