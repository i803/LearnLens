# LearnLens AI

**Understand the mistake. Fix the idea.**
An adaptive learning prototype that tells students *why* an answer went wrong, then helps them fix it. Built for Craft N Code 2026.

> Students get marks, not reasons. Teachers see repeated errors but have no time to reteach each student. LearnLens closes both gaps.

## What it does

`Upload work or pick a topic → see the evidence → possible misconception → 3-question check → focused lesson → practice → spaced retest → teacher view`

| For students | For teachers |
|---|---|
| Upload a worksheet (PDF or image) or pick a topic | Create a private class and share its code |
| Get a *possible* misconception, shown as a hypothesis with evidence | Watch students join, live |
| Confirm it with 3 fresh questions | See a student × concept mastery heatmap |
| Learn from a lesson grounded in 45 teaching notes (English, Hindi, Kannada) | Get the top shared misconceptions and a 10-minute reteach plan |
| Practise, then retest after 24 hours or more to confirm mastery | Export CSV and read student feedback |

Students join with a **nickname only**: no email, no password. Each browser keeps its own private data.

## Run it in 2 minutes

You need Python 3.11+ and Node.js 20.9+. **No API keys are required**: the demo works offline with built-in sample content.

**1. Backend** (terminal 1)

```bash
cd backend
python -m venv .venv
# Windows cmd:   .venv\Scripts\activate.bat
# PowerShell:    .venv\Scripts\Activate.ps1
# macOS/Linux:   source .venv/bin/activate
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8123
```

**2. Frontend** (terminal 2)

```bash
cd web
npm install
npm run dev
```

Open **http://localhost:3000**.

## Try it (about 3 minutes)

1. Open **Teacher view** (`/teacher`) and click **Create a private classroom code**. Copy the class code.
2. In a second browser window or profile, open **Join a class** (`/join`). Enter a nickname, the class code, and tick consent. The student appears in the teacher's roster within 10 seconds.
3. As the student, go to **My work**, click **Use bundled demo**, and follow the diagnosis, the 3-question check, the lesson and practice.
4. Back in the teacher view, the roster and heatmap now show that student's progress. Try **reteach plan**, **Export evidence** and the **/feedback** page.

Want a ready-made class? Use the sample class `CSE-A` with teacher key `demo-teacher-key`. **Its 8 students are synthetic.**

## Optional: turn on live AI and permanent storage

Copy `backend/.env.example` to `backend/.env` and fill in only what you need. Never commit this file.

| Goal | Set in `backend/.env` |
|---|---|
| Live AI | `OPENROUTER_API_KEY` (free model) and/or `GEMINI_API_KEY` |
| Data that survives restarts | `SUPABASE_URL`, `SUPABASE_SECRET_KEY`, then run `supabase/schema.sql` |

Without Supabase, data lives in memory and **a backend restart clears classes and students**.

## How it is built

- **Frontend:** Next.js, React, TypeScript, Tailwind
- **Backend:** FastAPI, Pydantic, PyMuPDF
- **AI (optional):** OpenRouter, Gemini
- **Storage:** in-memory by default, Supabase optional
- **Lessons:** local keyword search (BM25-style) over `content/notes.json`. No vector database.
- **Mastery:** a simple Bayesian-knowledge-tracing-style estimate with a 14-day forgetting half-life. A skill stays *provisional* until a successful retest at least 24 hours later.

## Check it

```bash
python -m pytest -q backend/tests      # backend tests
python scripts/verify_content_bundle.py # teaching-note integrity
cd web && npm run typecheck             # frontend types
```

## More detail

| | |
|---|---|
| How it works and demo script | [HOW_IT_WORKS_AND_DEMO_SCRIPT.md](HOW_IT_WORKS_AND_DEMO_SCRIPT.md) |
| Deploy to Vercel | [docs/DEPLOY_VERCEL.md](docs/DEPLOY_VERCEL.md) |
| Responsible AI | [docs/responsible-ai.md](docs/responsible-ai.md) |
| Design decisions and reuse | [docs/DECISIONS.md](docs/DECISIONS.md) |
| Evidence status | [docs/evidence.md](docs/evidence.md) |
| Judge deck | [docs/presentation/](docs/presentation/) |

## Ready to go live

| Area | What is in place |
|---|---|
| Privacy | Nickname only, explicit consent, and a one-click **delete my data** page |
| Access | Teacher key (stored hashed). Roster, heatmap and feedback are visible only to the class's own teacher |
| Abuse protection | Per-IP rate limits, real file-type checks on uploads (PDF/PNG/JPEG/WebP), 3.5 MB upload cap, browser security headers |
| Data | Separate data per browser. Add Supabase for storage that survives restarts |
| AI | Diagnoses are shown as hypotheses with their evidence. Teachers review before acting |

**Go-live checklist:** set the Supabase keys, set `FRONTEND_ORIGINS` to your site URL, add an AI key if you want live AI, then follow [docs/DEPLOY_VERCEL.md](docs/DEPLOY_VERCEL.md).

**Good to know:** the `CSE-A` class and the sample worksheet are synthetic demo data. Mastery scores are an educational estimate, not a grade.
