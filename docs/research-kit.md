# Research kit - collect real evidence before the pitch

**Status: not collected in this package.** Do not backfill invented responses. Obtain school/guardian/institution approval where relevant, explain data use, use nicknames, avoid collecting personal information, and record consent separately from feedback answers.

## Student pilot steps

1. Recruit a small opt-in group of students who are allowed to participate under school/event rules. Record the number invited, number who consented, number who completed each stage, and dates.
2. Use a fixed short pre-check on the selected topic, the LearnLens lesson/practice sequence, and a fresh post-check of comparable difficulty. Keep assessment items, scoring rubric and topic fixed before observing results.
3. Where feasible, use a delayed retest at least 24 hours later. Report paired results and how many students completed follow-up; do not interpret missing retests as successes.
4. Do not use school grades, medical data, account credentials, names, student IDs or identifiable answer sheets in screenshots or research files.
5. Obtain human review of AI diagnosis and question quality. Have two reviewers label a portion of worksheet items independently and report agreement before claiming tag accuracy.

## Student questionnaire (optional, 1-5 scale)

Ask participants to rate: (1) I understood why I made the mistake; (2) the lesson matched my mistake; (3) the lesson language was clear; (4) I could use the explanation to solve a new question; (5) I would use the tool again. Offer “prefer not to answer,” an optional free-text box, and a way to withdraw. Report denominator and response count for every score.

## Teacher interview prompts

- What do you currently do after seeing repeated errors on a worksheet?
- Which information would make a reteach decision faster or better?
- Are the misconception labels understandable and educationally meaningful?
- What would you need to verify before trusting a heatmap or reteach suggestion?
- What privacy or school-policy requirements would block a real pilot?
- Which output was helpful, confusing, wrong, or missing?

## Worksheet labelling protocol

Use the JSONL schema in `eval/README.md`. Two reviewers should label: extracted question/answer match, marks/rubric match when a trusted key exists, misconception tag, whether human review is required, and any unsafe/unsupported claim. Adjudicate disagreements before scoring. Preserve the original worksheet only if approval requires it; the scoring dataset should be redacted/de-identified. Do not treat a model-generated teacher feedback field as ground truth.
