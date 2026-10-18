# Evaluation harness

`run_eval.py` reads one JSON object per line. It is suitable for the synthetic smoke set now and for a future consented, de-identified, human-labelled set after review.

## Record shape

```json
{"id":"WS-001-Q1","synthetic":false,"labelled_by":"Reviewer A+B adjudicated","question":{"questionText":"...","studentAnswer":"...","teacherFeedback":"...","errorType":"conceptual","skill":"..."},"expectedTag":"interval_endpoint_inclusion","predictedTag":"interval_endpoint_inclusion","expectedMarks":1,"predictedMarks":1,"processingMs":412,"providerOk":true,"needsHumanReview":false}
```

`predictedTag` may be omitted to exercise the current local `infer_misconception` rules. Do not use a generated diagnosis as the gold label. Each record must clearly indicate whether it is synthetic. The script prints tag accuracy, macro/per-tag F1, marks MAE when both mark fields exist, median/p95 processing time when logged, provider success rate when logged, and human-review flag rate. It does not create missing live measurements.

## Run

```bash
python eval/run_eval.py --input eval/gold/synthetic_smoke.jsonl
python eval/run_eval.py --input /path/to/human_labelled.jsonl --output eval/results/human_eval.json
```

The results folder is ignored by Git to prevent accidental committing of student data. Do not store identifiable worksheets in this repository. Keep raw source files separately under the approved privacy protocol; only use redacted/de-identified labels in the evaluation input.

## Independent annotator agreement

Before computing prediction metrics, two reviewers should label a subset independently, without seeing LearnLens predictions. Use `eval/templates/annotator-agreement-template.jsonl` as a shape example (replace every placeholder first; do not evaluate the placeholder file). Compute raw agreement and Cohen's kappa with:

```bash
python eval/compare_annotators.py --input /path/to/finished_double_labels.jsonl --output eval/results/annotator_agreement.json
```

After disagreements are adjudicated by an appropriate subject reviewer, convert the frozen final labels into the schema above for `run_eval.py`. Keep human-label files outside the public repository if they could expose student work; use only consented/de-identified snippets. Small samples and class imbalance can make kappa unstable, so report label counts and disagreements too.
