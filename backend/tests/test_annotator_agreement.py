from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
EVAL = ROOT / "eval"
if str(EVAL) not in sys.path:
    sys.path.insert(0, str(EVAL))
from compare_annotators import compare


def test_compare_annotators_perfect_agreement():
    rows = [
        {"id": "1", "annotatorA": "tag_a", "annotatorB": "tag_a"},
        {"id": "2", "annotatorA": "tag_b", "annotatorB": "tag_b"},
        {"id": "3", "annotatorA": "tag_a", "annotatorB": "tag_a"},
    ]
    result = compare(rows)
    assert result["nDoubleLabelled"] == 3
    assert result["percentAgreement"] == 1.0
    assert result["cohensKappa"] == 1.0
    assert result["disagreementCount"] == 0


def test_compare_annotators_surfaces_disagreements():
    rows = [
        {"id": "1", "annotatorA": "tag_a", "annotatorB": "tag_a"},
        {"id": "2", "annotatorA": "tag_b", "annotatorB": "tag_a"},
    ]
    result = compare(rows)
    assert result["percentAgreement"] == 0.5
    assert result["disagreementCount"] == 1
    assert result["disagreements"][0]["id"] == "2"
