#!/usr/bin/env python3
"""Repeatable evaluation harness for human-labelled worksheets or synthetic smoke cases.

Each input JSONL record must include id, expectedTag, question, and synthetic.
Optional fields: predictedTag, expectedMarks, predictedMarks, processingMs,
providerOk, needsHumanReview, labelled_by. If predictedTag is absent, the local
misconception rules are run against `question`.

The script never classifies synthetic data as real evidence. Do not use its
synthetic smoke scores in a pitch as model accuracy or classroom impact.
"""
from __future__ import annotations
import argparse, json, sys, statistics
from collections import Counter
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
from app.notes import infer_misconception  # noqa: E402


def prf(tp: int, fp: int, fn: int) -> tuple[float,float,float]:
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2*precision*recall/(precision+recall) if precision+recall else 0.0
    return tuple(round(v, 4) for v in (precision, recall, f1))


def evaluate(rows: list[dict]) -> dict:
    tagged=[]
    per_tag: dict[str,dict[str,int]]={}
    for row in rows:
        q=row.get("question", {})
        predicted=str(row.get("predictedTag") or infer_misconception(q))
        expected=str(row.get("expectedTag") or "other")
        tagged.append((expected,predicted))
        for tag in set([expected,predicted]):
            m=per_tag.setdefault(tag,{"tp":0,"fp":0,"fn":0,"support":0})
            if expected==tag: m["support"]+=1
            if expected==tag and predicted==tag: m["tp"]+=1
            elif expected!=tag and predicted==tag: m["fp"]+=1
            elif expected==tag and predicted!=tag: m["fn"]+=1
    total=len(rows)
    correct=sum(a==b for a,b in tagged)
    metric_rows={}
    for tag,m in sorted(per_tag.items()):
        p,r,f1=prf(m["tp"],m["fp"],m["fn"])
        metric_rows[tag]={"precision":p,"recall":r,"f1":f1,"support":m["support"]}
    macro_f1=round(statistics.mean([v["f1"] for v in metric_rows.values()]),4) if metric_rows else 0.0
    mark_errors=[]
    for row in rows:
        if row.get("expectedMarks") is not None and row.get("predictedMarks") is not None:
            mark_errors.append(abs(float(row["expectedMarks"])-float(row["predictedMarks"])))
    latencies=[float(r["processingMs"]) for r in rows if r.get("processingMs") is not None]
    provider_states=[bool(r["providerOk"]) for r in rows if r.get("providerOk") is not None]
    review=[bool(r.get("needsHumanReview")) for r in rows]
    all_synthetic=all(bool(r.get("synthetic",True)) for r in rows)
    labelled_by={str(r.get("labelled_by", "")).strip() for r in rows if str(r.get("labelled_by", "")).strip()}
    if all_synthetic:
        evidence_type="synthetic smoke test - not human evaluation"
    elif len(labelled_by)==1 and "" not in labelled_by:
        evidence_type=f"human-labelled set (labelled by: {next(iter(labelled_by))}) - inspect sampling and inter-rater agreement"
    else:
        evidence_type="mixed or incompletely documented labels - not pitch-ready evidence"
    result={
      "createdAt":datetime.now(timezone.utc).isoformat(),
      "evidenceType":evidence_type,
      "isSyntheticOnly":all_synthetic,
      "n":total,
      "tagAccuracy":round(correct/total,4) if total else None,
      "macroF1":macro_f1,
      "perTag":metric_rows,
      "marksMAE":round(statistics.mean(mark_errors),4) if mark_errors else None,
      "processingMs":{"n":len(latencies),"median":round(statistics.median(latencies),2) if latencies else None,"p95":round(sorted(latencies)[max(0, int(0.95*len(latencies))-1)],2) if latencies else None},
      "provider":{"n":len(provider_states),"successRate":round(sum(provider_states)/len(provider_states),4) if provider_states else None},
      "humanReviewFlagRate":round(sum(review)/len(review),4) if review else None,
      "warning":"Synthetic rule smoke tests are not model benchmarks, field validation, classroom impact evidence, or an accuracy claim." if all_synthetic else "Before reporting these figures, document collection consent, worksheet selection, annotator protocol, inter-rater agreement, and failure handling."
    }
    return result


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="JSONL file of labelled examples")
    ap.add_argument("--output", help="Optional path for results JSON; defaults to stdout only")
    args=ap.parse_args()
    path=Path(args.input)
    if not path.exists(): ap.error(f"Input does not exist: {path}")
    rows=[]
    for i,line in enumerate(path.read_text(encoding="utf-8").splitlines(),1):
        if not line.strip(): continue
        try: row=json.loads(line)
        except json.JSONDecodeError as exc: ap.error(f"Invalid JSON on line {i}: {exc}")
        if not row.get("id") or "expectedTag" not in row or not isinstance(row.get("question"),dict): ap.error(f"Line {i} needs id, expectedTag, and question object")
        rows.append(row)
    result=evaluate(rows)
    text=json.dumps(result,indent=2,ensure_ascii=False)
    if args.output:
        out=Path(args.output);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(text+"\n",encoding="utf-8")
    print(text)

if __name__=="__main__": main()
