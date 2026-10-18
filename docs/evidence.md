# Evidence and validation status

This file distinguishes implemented product scaffolding from evidence that still has to be collected. **Nothing in this section should be presented as a completed user study.**

| Evidence item required by the team split | Status in this package | Next action |
|---|---|---|
| Student survey | PENDING | Run opt-in survey using `docs/research-kit.md`; report count and response rate |
| Student/teacher interviews | PENDING | Conduct real interviews with consent; summarize anonymized themes and counterexamples |
| Misconception-tag accuracy on 15-20 human-labelled worksheets | PENDING | Label a consented/redacted set independently; adjudicate; run `eval/run_eval.py` |
| Extraction/analysis speed, cache speed and failure rate | PENDING | Use `processingMs`, provider status and error logs during repeated, same-environment tests |
| Before/after learning check | PENDING | Run comparable fixed assessments; report paired sample size, score changes, missing follow-ups and limitations |
| Delayed retest confirmation | PENDING | Measure completion after at least 24 hours, not immediate practice alone |
| Accessibility and translation review | PENDING | Test keyboard navigation, screen-reader labels, local speech voices and Kannada/Hindi lessons with fluent reviewers |
| Production security/privacy review | PENDING | Review auth, authorization, retention, deletion, logging and deployment configuration |

## Synthetic engineering checks (not field evidence)

The repository contains eight hand-authored smoke cases in `eval/gold/synthetic_smoke.jsonl`, the synthetic CSE-A heatmap, and a sample PDF. These are deterministic developer fixtures used to exercise flows, not real learners, independent human annotations, benchmark samples, a pilot, or evidence of learning improvement.

## Suggested reporting format

For worksheet analysis: `N files`, `N questions`, exact annotation protocol, tag accuracy, macro-F1, per-tag precision/recall, reviewer agreement, human-review flag rate, extraction failures, median/p95 latency, cache hit rate, provider failure rate, and confidence intervals where the sample supports them. Include examples of wrong outputs as well as successes.

For learning change: report baseline and follow-up results for only paired participants, number lost to follow-up, topic and test design, average/median absolute change, distribution, and risks of practice effects. Avoid causal language unless the study design supports it.
