#!/usr/bin/env python3
"""Verify canonical and Vercel backend content copies are in sync and structurally valid."""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    canonical_notes = ROOT / "content" / "notes.json"
    canonical_tags = ROOT / "content" / "misconceptions.json"
    deployed_notes = ROOT / "backend" / "content" / "notes.json"
    deployed_tags = ROOT / "backend" / "content" / "misconceptions.json"
    if canonical_notes.read_bytes() != deployed_notes.read_bytes():
        raise SystemExit("FAIL: backend/content/notes.json differs from canonical content/notes.json")
    if canonical_tags.read_bytes() != deployed_tags.read_bytes():
        raise SystemExit("FAIL: backend/content/misconceptions.json differs from canonical content/misconceptions.json")
    notes = load(canonical_notes)
    tags = load(canonical_tags)
    note_ids = [row.get("id") for row in notes]
    tag_ids = [row.get("id") for row in tags]
    if len(note_ids) != len(set(note_ids)):
        raise SystemExit("FAIL: duplicate note IDs")
    if len(tag_ids) != len(set(tag_ids)):
        raise SystemExit("FAIL: duplicate misconception IDs")
    if not all(row.get("id") and row.get("title") and row.get("content") for row in notes):
        raise SystemExit("FAIL: every note must have an ID, title, and content")
    if not all(row.get("attribution") and row.get("license") for row in notes):
        raise SystemExit("FAIL: every note must disclose attribution and license/review status")
    draft_notes = [row for row in notes if "AI-assisted teaching-note draft" in str(row.get("attribution", ""))]
    if len(draft_notes) != 13:
        raise SystemExit(f"FAIL: expected 13 explicitly labelled AI-assisted draft notes, got {len(draft_notes)}")
    if not all("review pending" in str(row.get("attribution", "")).lower() for row in draft_notes):
        raise SystemExit("FAIL: AI-assisted draft notes must visibly indicate review is pending")
    if not all(row.get("id") and row.get("label") and row.get("reteach") for row in tags):
        raise SystemExit("FAIL: every misconception must have an ID, label, and reteach suggestion")
    print(f"PASS: {len(notes)} lesson notes; {len(tags)} misconception categories; unique IDs; Vercel bundle copies match.")


if __name__ == "__main__":
    main()
