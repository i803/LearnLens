# Hackathon submission checklist and short answers

## Links to fill in after hosting/submission

- Public repository: **[ADD TEAM REPOSITORY URL]**
- Hosted demo: **[ADD DEPLOYED APP URL]**
- Demo video: **[ADD VIDEO URL]**
- Slide deck: local file `docs/presentation/LearnLens_AI_Judge_Deck.pptx` / PDF companion
- Team members and roles: **[ADD VERIFIED NAMES + ACTUAL CONTRIBUTIONS]**
- AI / starter-code acknowledgements required by event rules: **[FILL USING ACTUAL TOOLS AND SOURCE LICENSES]**

Do not invent a URL or say any external form was submitted from this workspace. Check hackathon rules for whether starter-project reuse and AI-assisted work must be disclosed.

## What problem does LearnLens solve?

Students often receive a score or correction without understanding the misconception that caused the mistake. LearnLens turns worksheet or quiz evidence into a tentative learning-gap hypothesis, verifies it with new questions, offers a targeted lesson and practice, and tracks whether a delayed retest supports improved mastery. A teacher view surfaces concept-level patterns to help plan a short reteach.

## What is technically distinctive?

The prototype combines a structured misconception taxonomy, local BM25-style retrieval over 32 original notes plus 13 labelled AI-assisted draft notes pending team/educator review, explicit note-source displays, two optional AI-provider paths with fallback handling, a file-fingerprint result cache scoped per student, and an interpretable BKT-inspired mastery update. Mastery remains provisional until a successful spaced retest. Teachers can inspect a heatmap, review the most frequent misconception tags, request a ten-minute reteach-plan draft and export a CSV.

## What evidence supports impact?

No real pilot or measured learning gain is claimed in this package. The sample worksheet and CSE-A heatmap are synthetic fixtures for repeatable software demos. The next validation milestone is a consented pilot with 15-20 human-labelled worksheets, independently reviewed misconception labels, provider/latency/failure logs and paired before/after plus delayed-retest outcomes.

## Questions judges may ask

**Is it a grading engine?** No. Extracted marks can be incorrect; outputs include confidence/human-review flags and should be reviewed by a teacher. The current system is a learning-support prototype.

**Is this real RAG?** It retrieves relevant snippets from the bundled notes with a local BM25-style lexical ranker and returns IDs/snippets. It does not pretend that a vector database, embedding API or internet citations power the current retrieval path.

**Do you have proof that learning improved?** Not yet. The package explicitly marks surveys, interviews, human-labelled worksheet accuracy and before/after measures as pending.

**What happens without API keys or during an outage?** The app uses deterministic offline content where it has trusted bundled coverage. For unsupported topics it reports that trusted offline content is unavailable instead of fabricating a sourced answer.

**What would you do next?** Complete a privacy-approved pilot, validate label agreement and extraction, assess Hindi/Kannada content with fluent reviewers, strengthen teacher authentication/authorization, and deploy with tested monitoring and deletion controls.


## Short video + hosted demo

Before submission, complete [`DEPLOY_VERCEL.md`](DEPLOY_VERCEL.md), test the live URL in an incognito session, and record the real website using [`video-demo-script.md`](video-demo-script.md). Replace any submission-form placeholders with the actual deployed URL and exported video link/file. These files do not mean a deployment or upload has already occurred.
