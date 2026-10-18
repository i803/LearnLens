from __future__ import annotations
import json, math, re
from pathlib import Path
from typing import Any

# In the full repository, data lives at <repo>/content. When backend/ is
# deployed as the Vercel project root, it is bundled at <function-root>/content.
_HERE = Path(__file__).resolve()
_CANDIDATE_CONTENT_DIRS = [
    _HERE.parents[2] / "content",  # local monorepo checkout
    _HERE.parents[1] / "content",  # Vercel project rooted at backend/
]
_CONTENT_DIR = next((candidate for candidate in _CANDIDATE_CONTENT_DIRS if candidate.is_dir()), _CANDIDATE_CONTENT_DIRS[0])
NOTES_PATH = _CONTENT_DIR / "notes.json"
MISCONCEPTIONS_PATH = _CONTENT_DIR / "misconceptions.json"

def _load(path: Path, fallback: list[dict[str, Any]]) -> list[dict[str, Any]]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else fallback
    except (OSError, json.JSONDecodeError):
        return fallback

NOTES = _load(NOTES_PATH, [])
MISCONCEPTIONS = _load(MISCONCEPTIONS_PATH, [])
TOKEN_RE = re.compile(r"[a-z0-9]+")

def tokenize(value: str) -> list[str]:
    return TOKEN_RE.findall(value.lower())

def search_notes(query: str, limit: int = 4) -> list[dict[str, Any]]:
    """Small BM25-style retrieval over the bundled notes; no embedding or paid service needed."""
    if not NOTES:
        return []
    terms = tokenize(query)
    if not terms:
        return []
    docs = []
    for note in NOTES:
        text = " ".join(str(note.get(k, "")) for k in ("title", "subject", "topic", "content"))
        toks = tokenize(text)
        docs.append((note, toks))
    avgdl = sum(len(t) for _, t in docs) / max(1, len(docs))
    n = len(docs)
    scores = []
    for note, toks in docs:
        tf: dict[str, int] = {}
        for token in toks:
            tf[token] = tf.get(token, 0) + 1
        score = 0.0
        for term in set(terms):
            df = sum(1 for _, other in docs if term in other)
            idf = math.log(1 + (n - df + 0.5) / (df + 0.5))
            freq = tf.get(term, 0)
            if freq:
                k1, b = 1.5, 0.75
                score += idf * (freq * (k1 + 1)) / (freq + k1 * (1 - b + b * len(toks) / max(avgdl, 1)))
        # Exact concept/topic matches should rank ahead of incidental token matches.
        labels = tokenize(f"{note.get('title','')} {note.get('topic','')}")
        score += 1.25 * sum(1 for t in set(terms) if t in labels)
        if score > 0:
            scores.append((score, note))
    scores.sort(key=lambda pair: pair[0], reverse=True)
    return [dict(note, score=round(score, 3), snippet=str(note.get("content", ""))[:240]) for score, note in scores[:limit]]

def get_misconception(tag: str) -> dict[str, Any] | None:
    return next((item for item in MISCONCEPTIONS if item.get("id") == tag), None)

def misconception_prompt() -> list[dict[str, Any]]:
    return [{"id": m["id"], "label": m["label"], "conceptIds": m.get("conceptIds", [])} for m in MISCONCEPTIONS]

def infer_misconception(question: dict[str, Any]) -> str:
    candidate = str(question.get("misconceptionTag") or "").strip()
    if candidate and get_misconception(candidate):
        return candidate
    value = " ".join(str(question.get(k, "")) for k in ("questionText", "studentAnswer", "teacherFeedback", "skill", "conceptName", "errorType")).lower()
    normal = re.sub(r"\s+", " ", value)
    scores: dict[str, float] = {}

    def add(tag: str, amount: float = 1.0) -> None:
        scores[tag] = scores.get(tag, 0.0) + amount

    # Specific cues score more strongly than broad terms like "interval" or "intersection".
    if any(x in normal for x in ("right endpoint", "left endpoint", "endpoint", "bracket", "parenthesis", "open interval", "closed interval", "endpoint inclusion", "endpoint excluded", "endpoint included", "≤", "<=", "<=")):
        add("interval_endpoint_inclusion", 3.0)
    elif "interval" in normal and any(x in normal for x in ("included", "excluded", "open", "closed")):
        add("interval_endpoint_inclusion", 2.0)

    if any(x in normal for x in ("double-count", "double count", "counted the overlap twice", "count the overlap twice", "overlap twice", "subtract the intersection", "cardinality formula", "n(x union y)", "n(a union b)", "union-cardinality")):
        add("union_overlap_double_count", 3.0)
    if "cardinality" in normal and ("union" in normal or "intersection" in normal):
        add("union_overlap_double_count", 1.5)
    if "intersection" in normal:
        add("union_overlap_double_count", 0.25)

    if any(x in normal for x in ("difference direction was reversed", "reversed the difference", "a-b", "a - b", "a minus b", "kept values in b that are not in a", "in b not in a", "not in b")):
        add("difference_direction_reversed", 3.0)

    if any(x in normal for x in ("no natural number lies", "empty set", "set is empty", "is empty", "singleton", "no element", "no elements")):
        add("empty_vs_singleton", 2.0)
    if "empty" in normal and any(x in normal for x in ("one element", "single element", "not empty")):
        add("empty_vs_singleton", 2.0)

    if any(x in normal for x in ("finite vs infinite", "finite or infinite", "finite/infinite", "infinite points", "infinitely many", "finite because", "infinite because", "bounded interval")):
        add("finite_vs_infinite", 2.5)
    if "finite" in normal and "infinite" in normal:
        add("finite_vs_infinite", 2.0)

    if any(x in normal for x in ("negative root", "negative solution", "omitted the negative", "forgot the negative", "only positive root", "only x=", "both roots")):
        add("negative_solution_omitted", 3.0)
    if ("x²" in normal or "x^2" in normal or "squared" in normal) and "root" in normal and "negative" in normal:
        add("negative_solution_omitted", 2.5)

    if any(x in normal for x in ("ignored the domain", "domain was ignored", "forgot to apply x in", "forgot the domain", "domain restriction", "x ∈ n", "x in n", "x ∈ z", "x in z")):
        add("set_builder_domain_ignored", 3.0)
    elif "domain" in normal and any(x in normal for x in ("set-builder", "set builder", "natural number", "integer", "condition")):
        add("set_builder_domain_ignored", 1.5)

    if "disjoint" in normal or "disjointness" in normal or "no common elements" in normal or "they share values" in normal:
        add("disjointness_confusion", 3.0)
    if "intersection is empty" in normal and any(x in normal for x in ("disjoint", "common elements")):
        add("disjointness_confusion", 2.0)

    if any(x in normal for x in ("sign error", "negative sign", "minus sign", "sign was reversed")):
        add("sign_error_algebra", 2.0)
    if any(x in normal for x in ("misread", "misreading", "misread the question", "asked for")):
        add("question_misread", 2.0)
    if any(x in normal for x in ("arithmetic error", "arithmetic slip", "calculation error", "careless calculation")) or question.get("errorType") in {"arithmetic", "careless"}:
        add("arithmetic_slip", 2.0)
    if any(x in normal for x in ("incomplete reasoning", "without justification", "did not justify", "procedure without reasoning")):
        add("procedure_without_reasoning", 2.0)

    if scores:
        return max(scores, key=lambda tag: (scores[tag], -next((i for i, item in enumerate(MISCONCEPTIONS) if item.get("id") == tag), 999)))
    if question.get("errorType") == "misreading":
        return "question_misread"
    if question.get("errorType") == "incomplete_reasoning":
        return "procedure_without_reasoning"
    return "other"
