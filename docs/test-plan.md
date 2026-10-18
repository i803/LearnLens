# Manual and automated QA plan

## Automated checks

- Python syntax: `python -m compileall -q backend/app`
- Backend tests: `python -m pytest -q backend/tests`
- Synthetic rule smoke evaluation: `python eval/run_eval.py --input eval/gold/synthetic_smoke.jsonl`
- Frontend type check and build: from `web/`, `npm run typecheck` and `npm run build`

## Manual end-to-end checks

1. Start FastAPI and Next.js with blank AI keys. `/health` should report the offline configuration, 45 teaching notes and 22 misconception categories.
2. Join class `CSE-A` with a nickname and consent; rejection should occur without consent or when a name looks like an email.
3. Analyze `sample_math_test.pdf`; result should show synthetic/bundled provider and the analysis should not require an API key.
4. Follow diagnosis -> verification -> lesson -> practice. Confirm answer checking is deterministic and no fake lesson streaming endpoint is advertised.
5. Switch lesson language, read aloud, confirm note IDs/snippets and view provisional mastery state.
6. Before 24 hours, a retest cannot confirm the concept. After a due-time test simulation in an explicitly enabled test environment, a correct retest can confirm it. Keep `DEMO_TIME_TRAVEL=false` in ordinary usage.
7. Local clean checkout only: load CSE-A with the demo key; without it, access is denied. The heatmap labels all 8 students as synthetic. In real-data mode or any hosted deployment, CSE-A must return not found and no synthetic rows may be shown. Create a real class, join it from a second browser, and test roster refresh/CSV export. Generate a fallback reteach plan with no provider keys.
8. Create a separate class, record the private key securely, join it with a nickname and test heatmap authorization.
9. Use privacy deletion for a joined user; local profile/session keys should be cleared and the configured database/cache deletion result shown. A production rollout still requires verified backups/logs/retention behavior.
10. With valid API keys in a safe local environment, check both providers, provider failure/retry, provider status badges, cache hit behavior and invalid model JSON. Do not commit logs or keys.

## Known limitations

The CSE-A data are synthetic and local-only. Any `.env` file and every hosted deployment must disable them. In-memory class/session state is lost on restart without Supabase; hosted classroom operations should be tested with Supabase configured. The two-provider paths cannot be fully tested unless the corresponding keys/quota are available. Local-language coverage is intentionally incomplete and should be reviewed by fluent speakers.
