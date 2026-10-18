# Validation status — LearnLens AI score upgrade

Last checked: 2026-10-18 (environment clock; confirm date if exporting later).

## Passed in this workspace

- **Backend tests:** 23 passed.
- **Content data integrity:** 45 lesson notes and 22 misconception categories; unique IDs; canonical content and Vercel backend copies are byte-for-byte identical.
- **Source provenance:** all notes disclose attribution and license/review status; the 13 added AI-assisted drafts are explicitly marked review-pending.
- **Retrieval regression:** added notes are returned in top-3 results for selected algebra, determinant, units, matrix operation and set-operation queries.
- **Backend-root deployment simulation:** loading the copied `backend/` project as its own root loaded all 45 notes and 22 categories.
- **Frontend syntax transpilation:** 40 `.ts`/`.tsx` source files transpiled without syntax diagnostics. This checks syntax only, not semantic type errors.
- **Synthetic smoke evaluator:** 8/8 hand-authored rule fixtures matched. The bundled JSON output explicitly says synthetic-only; this is not a real-world accuracy result.
- **Credential scan:** no common OpenRouter, Google, Supabase-secret or private-key patterns matched in the source files at packaging time; no populated `.env` file is included.

## Not yet verified

- A clean frontend dependency install, full `npm run typecheck`, and production `npm run build` could not be completed here because package installation did not finish in this environment.
- A real Vercel deployment, live hosted URL, production environment-variable configuration, and browser end-to-end walkthrough have not been completed from this workspace.
- No real student pilot, human-labelled prediction benchmark, teacher interview or learning-gain measurement has been conducted.
- The 13 new AI-assisted teaching-note drafts still require review by the team/educator and licensing confirmation before external reuse.

## Before submission

Run in `web/` on a machine with package-registry access:

```bash
npm ci
npm run typecheck
npm run build
```

Then deploy and follow `DEPLOY_VERCEL.md`, test the deployed app in an incognito browser, record the real website using `video-demo-script.md`, and watch the exported 30–45 second video once before uploading. Do not tell judges the app is live until the URL has been opened and its main flow has passed those checks.
