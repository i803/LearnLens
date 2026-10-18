> **Local-only demo note:** This script uses synthetic `CSE-A` data and applies only to a clean local checkout with no `.env` file or service credentials. Do not follow its CSE-A steps on Vercel or in a configured checkout; deployed teacher pages must use a real class created for the test.

# Five-minute judge demo script

## 0:00-0:30 — The problem

“Students often receive a mark without a precise explanation of the underlying misconception. LearnLens tries to turn work into evidence for the next teaching step. It does not give grades; it suggests a possible gap that must be verified.”

## 0:30-1:00 — Join a class

Open **Join a class**, enter nickname `Blue Falcon`, class code `CSE-A`, select Kannada or English, and tick the consent box. Explain that CSE-A contains synthetic students created for a repeatable demonstration, not real pilot records.

## 1:00-2:00 — Analyse work

Open **My work → Use bundled demo**. The sample is explicitly marked synthetic. Show extracted questions, marks and flags. Explain that in live mode the free-tier provider may be used; with no keys the bundled demo path keeps the walk-through reproducible. Do not claim the synthetic analysis is an accuracy result.

## 2:00-3:10 — Diagnose and learn

Follow the possible learning gap to fresh verification questions, then open the focused lesson. Point to the retrieved note IDs/snippets, choose Kannada or Hindi, and use browser read-aloud. Explain that the 45-note starter library contains 32 original notes and 13 labelled AI-assisted drafts pending team/educator review; retrieved snippets are explainable starter content, not independently reviewed textbook citations. For the required short submission video, follow `video-demo-script.md` instead of this five-minute walkthrough.

## 3:10-4:05 — Practice and delayed retest

Answer a practice question and show that mastery is **provisional**. Explain that the model uses a transparent BKT-inspired probability update and requires a correct retest after the 24-hour interval before the concept is marked confirmed. If the event allows only a live demo, do not pretend a real 24-hour interval elapsed. Do not switch on demo time travel unless the judge asks to see that controlled test.

## 4:05-5:00 — Teacher workflow

Open **Teacher view**. Show the CSE-A heatmap, “P” provisional flags, top misconception tags, the ten-minute reteach-plan draft and CSV export. Note the synthetic-data banner. Show the “Create a real classroom code” form and explain that the teacher key is shown once and only a hash is stored.

## Closing statement

“The code and demo flows are packaged; the learning-impact evidence is not complete. We still need an approved pilot, 15-20 independently human-labelled worksheets, inter-rater agreement, provider reliability measurements, local-language review, and a production security review. We prefer to show that gap honestly rather than invent numbers.”
