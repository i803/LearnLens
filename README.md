# LearnLens AI — Craft N Code 2026

LearnLens AI is an adaptive learning prototype for students who need help understanding *why* an answer went wrong. It connects evidence from a worksheet or quiz to a possible misconception, a targeted lesson, practice, a delayed retest, and a teacher-facing view of class-level learning signals.

## 1. Problem and user

Students often receive marks or a correct answer without a clear explanation of the concept they misunderstood. Teachers may see repeated errors across a class but have limited time to create a reteach plan for every individual.

**Primary users:** students practising mathematics and teachers reviewing concept-level patterns. The included classroom heatmap is synthetic demonstration data. It is not evidence collected from real students.

## 2. How it works

The central learning loop is:

`Upload work or choose topic → inspect evidence → suggest misconception → verify with fresh questions → retrieve a focused lesson → practise → wait for spaced retest → update provisional/confirmed mastery → review teacher heatmap`

- **Worksheet analysis:** extracts questions/answers from a PDF or image, then returns structured results. A deterministic bundled sample is available when the provided demo worksheet is used without live AI credentials.
- **Misconception diagnosis:** uses a curated tag library and rule-based signals as a fallback. Diagnoses are hypotheses, not grades or formal assessments.
- **Grounded lessons:** retrieves relevant snippets from 45 bundled teaching notes (32 original notes plus 13 AI-assisted drafts marked for review) using a local BM25-style lexical search. Source note IDs and snippets are returned with the lesson. The notes are a starter knowledge base, not independently reviewed textbook material. The 13 newly added algebra/matrix/units/reasoning notes are labelled AI-assisted drafts and need team/educator review and licensing confirmation before external reuse.
- **Languages and access:** English, Hindi and Kannada lesson options are provided where vetted bundled fallback text exists; browser speech synthesis offers read-aloud. AI-generated translations and browser voices can be wrong or unavailable.
- **Mastery:** a small Bayesian Knowledge Tracing-inspired update incorporates guessing/slipping assumptions and a 14-day retention half-life. A skill remains provisional until a successful retest at least 24 hours after the prior practice. This is an educational heuristic, not a validated psychometric model.
- **Classroom:** students join with a nickname, class code, selected language and explicit consent. Teachers can create a class, use a private teacher key, open a student-by-concept heatmap, export CSV and generate a ten-minute reteach-plan draft.

## 3. Data and AI used

- `content/notes.json` contains 45 maths teaching notes: 32 original starter notes and 13 clearly labelled AI-assisted drafts that still need team/educator review and licensing confirmation before external reuse. `content/misconceptions.json` contains 22 misconception categories with descriptions/signals and reteach suggestions.
- Retrieval is local lexical BM25-style ranking. No embedding API or external search is required for that path. The included SQL schema leaves room for future source chunks, but this prototype does not claim that a vector database is powering lesson retrieval.
- OpenRouter is configured for `openrouter/free` only; optional Gemini is the second provider. Both require user-supplied server-side keys and the provider account must be eligible for the chosen model/quota. Model access and free quotas can change.
- If no provider is configured, the project uses domain-specific deterministic fallback content where available and clearly returns an error for unsupported offline topics rather than inventing a supposedly sourced lesson.
- Supabase persistence is optional for local development. Without server credentials the app uses in-memory learning records plus a local SQLite result cache, so restarts clear records. **For a reliable public Vercel demo of the full multi-step student flow, configure Supabase** because separate serverless invocations cannot be assumed to share memory. Cache entries are student-scoped; deletion attempts to purge that student's cache as well as saved records.
- The code does not rely on hidden data or claim use of private student records. The bundled eight-student CSE-A heatmap is fictional sample data for a repeatable judge demo.

## 4. How to run it

Requirements: Python 3.11+ and Node.js 20.9+ (Node 22 recommended for this Next.js version).

### A. Backend

From the project root, create a virtual environment, install dependencies and copy the safe template:

**Command Prompt**

```CMD
cd backend
python3 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
python -m uvicorn app.main:app --reload --port 8123
```

**macOS / Linux**

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
python -m uvicorn app.main:app --reload --port 8123
```

The safe template has blank API and database keys. The backend will still start for the demo. To enable live AI, add an eligible `OPENROUTER_API_KEY` (model must stay `openrouter/free` or a `:free` model) and/or `GEMINI_API_KEY` to `backend/.env`. To enable persistent database storage, add `SUPABASE_URL` and `SUPABASE_SECRET_KEY` and run `supabase/schema.sql` for a new project or `supabase/migration_hackathon.sql` for an existing schema. Never place the Supabase secret key or provider keys in browser code or commit them.

### B. Frontend

In a second terminal, from the project root:

```bash
cd web
npm install
npm run dev
```

Open `http://localhost:3000`. The Next.js catch-all API route forwards requests to `http://127.0.0.1:8123` by default. Set `AI_SERVICE_URL` in the frontend process only if the backend is hosted elsewhere.

### C. Repeatable checks

```bash
# From the project root after Python dependencies are installed
python -m compileall -q backend/app backend/index.py eval
python -m pytest -q backend/tests
python scripts/verify_content_bundle.py
python eval/run_eval.py --input eval/gold/synthetic_smoke.jsonl

# Frontend, from web/
npm run typecheck
npm run build
```

The supplied smoke JSONL is synthetic rule testing. Its metrics are not model accuracy, user-study results or classroom-impact evidence. For a human-labelled worksheet evaluation, create an explicitly consented and de-identified JSONL based on the template described in `docs/evidence.md` and use a separately documented annotation protocol.

### D. Judge demo

1. Start both servers and open the homepage.
2. Use **Join a class** with nickname `Blue Falcon`, code `CSE-A`, choose English/Kannada/Hindi and tick consent.
3. Open **My work → Use bundled demo**. The sample PDF is clearly labelled synthetic.
4. Follow the suggested diagnosis and verification, open the targeted lesson, use the language selector/read-aloud, then practise.
5. Open **Teacher view**. The default `CSE-A` heatmap uses fictional students; demo teacher key is `demo-teacher-key`. Generate the rule-based/AI reteach draft and export CSV.
6. Do not represent the sample heatmap or worksheet as real pilot data.


## 4A. Deploy for judges and record the short demo

- Follow [`docs/DEPLOY_VERCEL.md`](docs/DEPLOY_VERCEL.md) to deploy `backend/` and `web/` as two Vercel projects and configure the backend URL. This is a deployment guide, not proof that the project has already been hosted.
- Follow [`docs/video-demo-script.md`](docs/video-demo-script.md) to record a 40–43 second walkthrough of the actual deployed website. An SRT caption file is included at [`docs/video-demo-captions.srt`](docs/video-demo-captions.srt).
- Review [`docs/score-improvement-plan.md`](docs/score-improvement-plan.md) for evidence that can legitimately improve judging: a verified public deployment, human-labelled diagnosis evaluation, independent reviewer agreement, and delayed-retest tests.
- Vercel's request body limit means the hosted demo limits combined uploads to 3.5 MB. This guard is implemented in the upload screen.

## 5. AI tools and reused code

This update was built by extending and refactoring the uploaded LearnLens project; it was **not created from a blank repository during the hackathon**. The package's code and docs identify the added/changed components, and `docs/DECISIONS.md` records the reuse honestly. The ZIP does not include `.git` history, so it cannot prove when code was written or committed. The team should attribute any external starter code, libraries, icons, generated copy, and AI assistance according to the rules of its event.

The project uses Next.js, React, TypeScript, Tailwind CSS, FastAPI, Pydantic, PyMuPDF, Pillow, ReportLab, SQLite, optional Supabase REST/Postgres, and optional OpenRouter/Gemini APIs. See the package files and lockfiles for exact software versions. The project contains no live API credentials in its `.env.example`.

Judge-ready collateral is included at `docs/presentation/LearnLens_AI_Judge_Deck.pptx` and `.pdf`, with a live-demo script, research kit, evaluation harness, test plan, responsibility notes, and submission checklist under `docs/` and `eval/`.

## 6. Limits

- No real student pilot, educator interviews, survey, human-labelled worksheet accuracy study, before/after learning result, provider reliability benchmark, or field speed statistic is claimed in this package. Those evidence items are explicitly marked **PENDING** in `docs/evidence.md`.
- The class dashboard's eight demo students and the sample worksheet are synthetic. They must never be counted as a pilot or as evidence of learning gains.
- The misconception taxonomy and 45 teaching notes (including 13 AI-assisted drafts pending review) are a small first version. Accuracy and coverage are unvalidated; answers, lesson translations and generated reteach plans need teacher review.
- Kannada/Hindi are not complete translations of every concept in the offline content; some concepts deliberately fall back to an availability warning. Speech synthesis depends on browser/OS language voices.
- Mastery probabilities are heuristic and should not be used to assign course grades, rank students, make placement decisions, or replace professional teacher judgement.
- The in-memory backend is not production storage. On Vercel, separate function invocations may not share process memory and the `/tmp` SQLite cache is ephemeral; configure Supabase for durable class/progress records. A public school deployment also needs institution-approved privacy terms, tested authentication/authorization, rate limiting, upload scanning, backup/retention/deletion verification, monitoring, accessibility testing and robust concurrency controls.
- External deployment, a public repository link, a hosted demo, a submitted video, and hackathon-portal submission are not created by this local ZIP. Fill the link placeholders in `docs/submission.md` after hosting and submitting through your team's own accounts.
