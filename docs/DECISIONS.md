# Implementation decisions and provenance

- This ZIP is an extension/refactor of the uploaded LearnLens project, not a claim that all source was newly authored during the hackathon. The original archive already contained the main student workflow and APIs; the update split screens/routes, added classroom workflows, local retrieval, misconception taxonomy, provider fallback/cache, BKT-inspired spaced mastery, consent/privacy controls, tests and presentation/evidence scaffolding.
- This delivery ZIP does not include `.git` history. It cannot substantiate authorship timing or demonstrate that each contribution was committed by the correct teammate. The team should keep real version history and attribute reused/AI-assisted content under event rules.
- BM25-style lexical retrieval is selected for the bundled 45-note content so the demo can run without paid embeddings. Source IDs and snippets are exposed and the docs say the notes are not independently verified references.
- AI is optional and should degrade clearly. OpenRouter is restricted to the `openrouter/free` / `:free` model-name path; Gemini is optional. Account quotas, model availability and network failures remain external dependencies.
- The mastery update is explicitly called BKT-inspired, not a validated implementation of a classroom psychometric model. A correct answer alone cannot confirm mastery before the spaced retest due time.
- CSE-A roster and bundled worksheet are marked synthetic. No survey, interview, pilot, benchmark, speed result or pre/post learning result was fabricated.
- Teacher keys are generated from secure randomness and only the SHA-256 hash is intended to be stored for created classes. The current teacher auth is prototype-grade and must be hardened before use with a real school.
