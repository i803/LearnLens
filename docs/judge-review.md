# LearnLens AI — updated judge-style review

**Review type:** source/package desk review after the deployment and content-coverage upgrades. This is an estimate, not an official event score. The app has not been deployed from this package to a live Vercel account in this environment, and no real student pilot or human-labelled accuracy study has been run. The backend tests pass; a clean frontend dependency install and production Next.js build remain unverified because package access was unavailable in this environment.

## Indicative score: 70/100

| Criterion | Score | What is working | What limits the score |
|---|---:|---|---|
| Problem and target user | 8/10 | Clear student and teacher need; the app focuses on why a skill may be difficult and what to do next. | No real student/teacher discovery study yet. |
| Product functionality | 14/20 | Student work analysis, editable evidence, diagnosis/verification, lessons, practice/retest, teacher heatmap, reteach draft and CSV are wired in source; the bundled worksheet works offline in the backend test environment. | Browser-level end-to-end QA on the deployed instance is still pending. |
| Engineering and reproducibility | 15/20 | Source-separated frontend/backend, Vercel entrypoint, deployment guide, backend health check, content-bundle verifier, 23 passing backend tests, SQL schema and deployment smoke plan. | Vercel deployment and a full clean `npm ci` / `npm run typecheck` / `npm run build` have not been completed here. |
| AI quality and grounding | 12/15 | Local BM25-style retrieval now covers 45 starter notes (32 existing notes plus 13 AI-assisted drafts awaiting review) spanning sets, algebra, matrices/determinants, units, formula conditions, and mathematical reasoning; source IDs/snippets are exposed. | Notes and translations are not independently educator-reviewed; no human-labelled prediction metrics or provider reliability study. |
| Privacy and responsible design | 9/10 | Nickname/consent flow, data deletion path, server-side secrets, provisional mastery, human-review caveat and synthetic-data labels. | Prototype-level teacher access and storage need a real deployment security review; this is not school-ready data infrastructure. |
| Evaluation and impact | 4/15 | 21 backend tests, an eight-item clearly labelled synthetic smoke set, an annotation-agreement script, and a human-evaluation protocol template. | No human-labelled set, educator interviews, pilot, pre/post learning evidence or measured latency/reliability results. |
| Demo and communication | 8/10 | 40–43 second video script, caption file, deploy runbook, and existing judge materials. | Real hosted URL and recorded video file still need to be created/submitted by the team. |
| **Total** | **70/100** |  |  |

## The actions most likely to improve the score

1. **Deploy and verify the live product.** Follow `DEPLOY_VERCEL.md`, then complete all production smoke checks in an incognito browser. A README is not a hosted demo; provide judges with the actual URL.
2. **Record a 30–45 second video from the real site.** Use `video-demo-script.md` and `video-demo-captions.srt`. Keep the synthetic-data notice visible on the teacher dashboard. Never claim the site has been hosted until the URL has been tested.
3. **Run clean frontend checks.** On a machine with package registry access, run `cd web && npm ci && npm run typecheck && npm run build`. Fix every diagnostic before making the repo public or recording the final video.
4. **Collect valid evaluation evidence.** Use 15–20 consented, de-identified worksheet items, two independent subject-aware annotators, adjudicated final labels, and `eval/compare_annotators.py`. Freeze the labels before testing the model/rules. Report macro-F1 and per-tag precision/recall plus sample size and label counts.
5. **Test time-based mastery honestly.** Check early retest, due-time retest, failed delayed retest and successful delayed retest. A demo should show provisional mastery rather than simulating instant learning gains.
6. **Validate lesson retrieval and localization.** The package now checks retrieval for fractions, determinant signs, units, matrices and set operations. Have a mathematics educator and fluent Kannada/Hindi reviewers validate explanations before claiming instructional accuracy or complete localization.
7. **Use durable data for any public multi-user test.** Configure Supabase before expecting class/progress records to survive across Vercel function instances. Do not use real student data in a public demo without institution-approved policy and security controls.

## What can be claimed today

- The repository bundles **45 teaching notes** (32 existing notes plus 13 AI-assisted drafts clearly marked for review) and **22 misconception categories**; these are starter content, not independently validated sources.
- The Python backend test suite passed **23 tests** in this environment.
- The eight-case synthetic smoke evaluator returns 8/8 matches for its hand-authored rule fixtures; the exact output is saved in `eval/results/synthetic_smoke_result.json` and labelled synthetic-only. This is a software regression test only—not model accuracy, a real-world benchmark or evidence of learning gains.
- The local retrieval path is lexical BM25-style ranking over bundled note text. The package does not claim to use a deployed vector database for those results.
- The mastery update includes a heuristic forgetting curve and a 24-hour retest gate. It is not a validated psychometric model or a formal grade.

## Claims to avoid until measured

Do not claim validated accuracy, improved grades, learning gains, teacher adoption, time saved, production readiness, completed pilot results or audited privacy/security. Collect and document that evidence first.
