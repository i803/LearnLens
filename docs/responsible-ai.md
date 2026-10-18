# Responsible AI and student privacy

LearnLens provides learning hypotheses, not grades or diagnoses of a person. It must not replace a teacher or be used for high-stakes grading. Low-confidence handwriting, unclear symbols, estimated marks, and unknown misconception tags should be treated as review prompts. A student or teacher should correct misread evidence before relying on a lesson.

## Data minimization
- Student join asks for a nickname, a class code, a language choice, and consent; no email or password is requested.
- The browser must not receive a Supabase service/secret key. Keep secrets in `backend/.env` or a hosting provider's secret manager.
- Do not upload identifiable real worksheets without the student's/guardian's permission and a clear retention policy. Use synthetic worksheets for public demos.
- `POST /student/delete-data` requests deletion of a student's server-side records. Clear the corresponding `learnlens_*` values from browser local storage too. A production deployment should add stronger user verification and audited deletion status.
- The local SQLite cache stores parsed analysis results keyed by a one-way file fingerprint. Because its payload contains worksheet-derived information, treat the cache as sensitive and exclude the cache file from Git.

## AI limits
- Model output can misread handwriting, produce a mistaken misconception, or translate academic nuance poorly.
- Lesson citations are restricted to note IDs supplied from the bundled notes; the BM25 retriever is lexical search, not a vector database.
- A configured provider does not mean a request succeeded. UI status must distinguish live AI, saved results, and deterministic sample fallback.
- The Gemini provider is optional. Configure it only with an eligible free-tier account/model and monitor its quota/billing settings; never put provider keys in client code.
- Mastery is an internal probability estimate, not a validated psychometric score. It decays over time and remains provisional until a delayed retest is passed.

## Accessibility
Use keyboard navigation, labels for form controls, visible focus, readable contrast, browser text-to-speech where available, and English as a fallback. Kannada/Hindi text is machine- or template-generated and should be reviewed by fluent speakers before classroom use.
