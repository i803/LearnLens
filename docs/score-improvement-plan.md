# How to improve LearnLens AI's hackathon score

The most valuable next step is not adding more features at random. It is proving that the existing end-to-end learning loop works on the hosted site and measuring whether its diagnoses are reliable.

## Priority 1 — judge can actually use it

- Deploy both projects and add the real frontend URL plus a demo login/entry path to the submission form.
- Keep the bundled worksheet flow usable without a third-party AI key.
- Configure Supabase if progress/class records need to persist across serverless invocations.
- Run every item in `docs/DEPLOY_VERCEL.md` from an incognito browser after deployment.
- Record the 40-second site demo with the steps in `docs/video-demo-script.md`.

**Evidence to save:** public URL, video file, successful endpoint checks, deployed build logs, screenshot of sample analysis, screenshot of teacher heatmap with synthetic notice, and the date/browser used for smoke testing.

## Priority 2 — human-reviewed misconception quality

1. Recruit two reviewers who understand the relevant mathematics; get appropriate consent to use any work and remove names, IDs, school identifiers, handwriting metadata where feasible, and other personal information.
2. Build a small set of 15–20 representative questions/answers. Avoid selecting only easy examples. Include ambiguous handwriting, incomplete reasoning, common arithmetic slips, multiple errors, and cases where the right answer is paired with incorrect reasoning.
3. Both reviewers label the misconception independently without seeing LearnLens predictions. Record adjudication and a short rationale when labels disagree.
4. Use the same label taxonomy in `content/misconceptions.json`. Do not force a tag when the evidence is insufficient; mark the case as needing human review.
5. Run the prediction script only after freezing the labels. Report accuracy, macro-F1, per-label support/precision/recall, annotation agreement, and failure counts. Include difficult examples and limitations.

The current eight-case 100% smoke result is deliberately synthetic and team-authored. It is a software regression check, not accuracy evidence. Never advertise it as model accuracy.

## Priority 3 — show the learning loop, not just the UI

- Test that a learner's first practice keeps mastery provisional.
- Verify the 24-hour gate prevents early mastery confirmation.
- Verify a correct delayed retest can confirm a skill, while a failed retest stays provisional and reschedules review.
- If a real opt-in pilot is feasible, use equivalent pre/post assessments and report the paired sample size, score distribution, missing follow-ups, time interval, and limitations. Do not claim causation from an uncontrolled, tiny pilot.

## Priority 4 — content and accessibility review

- Have a mathematics educator review the note content, answer explanations, diagnosis labels, and reteach plans.
- Ask fluent Kannada and Hindi reviewers to inspect the translations; do not claim complete localization unless every learning flow has been reviewed.
- Test keyboard-only completion, focus order, visible error messages, screen reader labels, contrast, mobile layout, and text zoom.

## Priority 5 — make claims auditable

Every deck, README, video caption, and submission form should distinguish:

- **Implemented:** present in source code and testable.
- **Synthetic test:** deterministic fictional data for repeatable software checks.
- **Human-labelled result:** only a frozen dataset reviewed using a documented procedure.
- **Field/pilot evidence:** only actually collected, consented observations.

A better score comes from a reliable hosted demo, a focused story, strong error handling, and transparent evidence—not invented percentages or a larger list of unvalidated AI claims.
