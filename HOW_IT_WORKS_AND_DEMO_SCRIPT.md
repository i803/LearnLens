# LearnLens AI: how it works, and how to record the demo

## 1. How everything works

**Three pieces**
- `web/` is the Next.js front end. Every call goes to `/api/*`, which is proxied to the backend (`AI_SERVICE_URL`, default `http://127.0.0.1:8123`).
- `backend/` is FastAPI. It holds the learning logic, the mastery maths, the teaching-notes search and the AI calls.
- Storage is Supabase if configured. Otherwise it is in memory, so **restarting the backend wipes classes, students and feedback**.

**Who is who (identity)**
- No passwords. A student joins at `/join` with a nickname, a class code and consent, and gets a server-issued `stu_…` ID kept in that browser.
- A student who has not joined gets a private random per-browser ID (`stu_anon_…`). Their data is separate from everyone else's but belongs to no class, so the teacher cannot see them.
- A teacher creates a class at `/teacher`. They get a class code (`LL-XXXXX`, to share) and a teacher key (shown once, private). The key is sent as the `X-Teacher-Key` header.
- In a clean local checkout without a `.env` file, `CSE-A` with key `demo-teacher-key` is a labelled synthetic sample class. It is not real data and is disabled by any `.env` file and on all hosted deployments.

**The student learning loop**
1. Start from a topic (`/student/learn`) or by uploading a worksheet (`/student/work`).
2. Worksheet path: the AI extracts questions and answers, you review them (`/student/analysis`), then get a possible misconception (`/student/diagnosis`). It is a hypothesis, not a grade.
3. A 3-question check (`/student/verify`) uses fresh questions to confirm or reject the hypothesis.
4. A lesson (`/student/lesson`) is built from 45 bundled teaching notes, found by local keyword search. Hindi and Kannada are available.
5. Practice (`/student/practice`), then a spaced retest 24 hours or more later (`/student/retest`).
6. Mastery uses a Bayesian-knowledge-tracing-style update (guess 0.20, slip 0.10, learn 0.08) with a 14-day forgetting half-life. A skill stays **Provisional** until a successful retest at least 24 hours later, then becomes **Confirmed**.
7. `/student/progress` shows saved mastery. `/feedback` collects a rating and comments. `/student/privacy` deletes the student's data.

**AI and fallbacks:** OpenRouter (free model) first, optional Gemini second. With no keys it uses bundled deterministic content for the demo worksheet and the set-theory topics.

**Teacher view (`/teacher`)**
- In real-data mode it reopens only the class this browser saved; otherwise a teacher must enter their class code/key or create a class. Only an unconfigured local checkout automatically opens the sample class.
- **Class roster:** nickname, join time, language, answers recorded, last active, average mastery, status. A student appears when they join, and the page refreshes every 10 seconds.
- **Summary cards:** joined, started learning, answers recorded, class average.
- **Heatmap:** student × concept. Columns are the default concepts plus any topic a student actually studied. A cell with no answers yet shows "Not started", not 0%.
- **Also:** top misconceptions, a 10-minute reteach plan, CSV export, and the student feedback panel.

## 2. Setup before recording
1. Start the backend (`python -m uvicorn app.main:app --port 8123` in `backend/`) and the web app (`pnpm dev` or `npm run dev` in `web/`).
2. Set `OPENROUTER_API_KEY` in `backend/.env` for live AI. Without it, use the bundled sample worksheet and the Sets topics.
3. Open **two different browser profiles** (or one normal window and one private window), plus the teacher in a third window. This shows the separate-users point.
4. Do not restart the backend between takes unless you are using Supabase.
5. Record at 1080p with a screen recorder (OBS, or Win+G). Zoom the browser to about 110%. Use a mic, not laptop speakers. Rehearse once first.

## 3. Script (about 3 to 4 minutes)
| Time | Show | Say |
|---|---|---|
| 0:00 | Landing page | The problem: students get marks, not the reason they were wrong. Click the arrow on the snapshot card. |
| 0:20 | `/teacher`: create a class (name it, say your own name) | Teacher creates a private class and gets a code and a key. Point out the class code and the empty roster. |
| 0:45 | Window B: `/join`, nickname "Blue Falcon", the class code, tick consent | Students use nicknames, no email. Switch to the teacher window: **Blue Falcon appears in the roster within 10 seconds**. |
| 1:05 | Window C (second profile): join as "Green Owl" | A second student gets separate data. Roster shows two students. |
| 1:25 | Window B: `/student/work`, "use demo paper" | Upload a worksheet. The AI extracts the answers. Teacher reviews them, so the AI never grades. |
| 1:50 | Analysis, then Diagnosis | A possible misconception, kept as a hypothesis with evidence from questions 5 and 6. |
| 2:10 | 3-question check: answer, submit | Fresh questions confirm or reject it. |
| 2:30 | Lesson, then practice | A lesson grounded in teaching notes. Show the language switch and read-aloud. |
| 2:50 | `/student/progress` | Mastery is provisional until a spaced retest. Window C shows empty progress: separate users. |
| 3:05 | Teacher window | Roster now shows Blue Falcon's answers and average. Heatmap has a real row. Click "reteach plan". Show the CSV export. |
| 3:30 | `/feedback`, then the teacher feedback panel | Student feedback reaches the teacher. |
| 3:45 | `/student/privacy` | Delete-my-data and the privacy design. Close. |

**Tips:** keep each flow short; cut the recording at AI loading screens or say one line over them; mention honestly that the sample class is synthetic and the real class is the one you created; end on the teacher roster and heatmap because that is the strongest "this is real" moment.
