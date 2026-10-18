#!/usr/bin/env python3
"""Compare two independent human labelers using percent agreement and Cohen's kappa.

Input JSONL example:
{"id":"WS-01-Q1","annotatorA":"interval_endpoint_inclusion","annotatorB":"interval_endpoint_inclusion"}

Do not add predictions to this input before annotators freeze their labels. Use only
consented, de-identified samples. The script does not make the label judgments.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path


def compare(rows: list[dict]) -> dict:
    if not rows:
        raise ValueError("At least one double-labelled item is required")
    pairs=[]
    for i, row in enumerate(rows, 1):
        a=str(row.get("annotatorA", "")).strip()
        b=str(row.get("annotatorB", "")).strip()
        if not row.get("id") or not a or not b:
            raise ValueError(f"Row {i} must contain id, annotatorA, and annotatorB")
        pairs.append((a,b))
    labels=sorted({label for pair in pairs for label in pair})
    n=len(pairs)
    observed=sum(a==b for a,b in pairs)/n
    count_a={label:sum(a==label for a,_ in pairs) for label in labels}
    count_b={label:sum(b==label for _,b in pairs) for label in labels}
    expected=sum(count_a[label]*count_b[label] for label in labels)/(n*n)
    kappa=(observed-expected)/(1-expected) if expected < 1 else (1.0 if observed == 1 else 0.0)
    disagreements=[{"id":row["id"],"annotatorA":a,"annotatorB":b} for row,(a,b) in zip(rows,pairs) if a!=b]
    return {
        "nDoubleLabelled":n,
        "labelsSeen":labels,
        "percentAgreement":round(observed,4),
        "cohensKappa":round(kappa,4),
        "countsAnnotatorA":count_a,
        "countsAnnotatorB":count_b,
        "disagreementCount":len(disagreements),
        "disagreements":disagreements,
        "interpretationNote":"Report this with the sample size and label distribution. Kappa is sensitive to class prevalence; it is not a substitute for adjudication or domain review."
    }


def main() -> None:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="JSONL with id, annotatorA, annotatorB")
    parser.add_argument("--output", help="Optional output JSON path")
    args=parser.parse_args()
    path=Path(args.input)
    rows=[]
    for line_no,line in enumerate(path.read_text(encoding="utf-8").splitlines(),1):
        if not line.strip():
            continue
        try:
            row=json.loads(line)
        except json.JSONDecodeError as exc:
            parser.error(f"Invalid JSON on line {line_no}: {exc}")
        rows.append(row)
    try:
        result=compare(rows)
    except ValueError as exc:
        parser.error(str(exc))
    output=json.dumps(result,indent=2,ensure_ascii=False)
    if args.output:
        out=Path(args.output);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(output+"\n",encoding="utf-8")
    print(output)

if __name__ == "__main__":
    main()
