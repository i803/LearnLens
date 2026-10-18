# LearnLens AI — 40-second website demo video

**Goal:** show an end-to-end product journey in 40–43 seconds. This is a screen-recorded website demo, not a teacher presentation. Keep the real deployed website visible; do not use slides as a substitute for the working product.

## Setup before recording

- Deploy both frontend and backend and finish the checks in `docs/DEPLOY_VERCEL.md`.
- Open the website in a clean incognito window at 100% zoom; use a desktop viewport of about 1440×900 or 1280×800.
- Turn on Do Not Disturb and close unrelated tabs. Disable browser bookmarks and extensions from view.
- Make the browser window large enough that the main action and the result are readable. Keep the mouse still between clicks.
- Configure Supabase and verify the deployed app first. Create a real test classroom, join it from a separate browser with a test nickname and consent, and submit at least one learning activity so the teacher view contains only actual records created during this test. Do not expect or try to load the synthetic `CSE-A` class on the deployed site.
- Record at 1080p, 30 fps. Use a calm voiceover and burned-in captions. Keep the video between 30 and 45 seconds.

## Timeline, clicks, and voiceover (target ~42 seconds)

| Time | On screen / action | Voiceover |
|---|---|---|
| 0–4 s | Homepage; briefly show product name and primary learning loop. | “LearnLens AI helps students understand why an answer went wrong—not just what mark they lost.” |
| 4–9 s | Open **I have work I got wrong** and click **Use bundled demo**. Show the analyzing state briefly. | “I’ll start with a sample mathematics worksheet.” |
| 9–15 s | Show the analysis result: extracted work, suggested misconception and evidence/uncertainty. | “It extracts the work and suggests a possible misconception that the student can verify.” |
| 15–21 s | Open verification/diagnostic or the targeted lesson; briefly show a source-note reference. | “Then it checks understanding and retrieves a focused lesson from its bundled learning notes.” |
| 21–28 s | Show one practice question and the progress/provisional mastery message. | “Practice updates a provisional mastery estimate; confirmation waits for a delayed retest.” |
| 28–37 s | Open Teacher view and show the test classroom roster, saved learning activity, heatmap, reteach-plan draft, and CSV export control. Use only the real records created during setup. | “Teachers can spot class-level patterns from saved student activity and draft a short reteach plan.” |
| 37–42 s | Return to homepage or leave the full product visible with project name. | “LearnLens connects evidence, targeted learning, practice, and spaced review in one flow.” |

**Editing rule:** if your deployed UI takes longer to load, cut transitions—not safety labels or truthful source/evidence information. Don't claim measured accuracy, student improvement, or a real pilot unless you have actually collected that evidence.

## Export checklist

- [ ] Duration is 30–45 seconds.
- [ ] Hosted URL is visible at least once, or appears as a final caption.
- [ ] No API keys, environment variables, private student data, or personal browser information appear.
- [ ] The hosted teacher view contains only records created by the consenting test student(s); no synthetic teacher roster is present.
- [ ] Captions match the spoken words; check spelling and timing.
- [ ] The screen shows the actual deployed site, not a mock-up.
- [ ] Playback checked once after export; audio is audible and text legible on a phone.

## Suggested final caption

`LearnLens AI | From worksheet evidence to targeted learning | Teacher view uses saved test-class activity`
