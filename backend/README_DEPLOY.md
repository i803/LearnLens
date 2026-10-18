# Backend deployment notes

- Vercel backend project root: `backend/`.
- Entry point: `index.py`, exporting the FastAPI ASGI application as `app`.
- Runtime dependencies: `requirements.txt`.
- Curated content is mirrored in `backend/content/` so it is included when Vercel packages only this directory. The canonical content for development remains in the repository's top-level `content/`; keep both copies in sync when editing lesson notes or misconception tags.
- Set `LEARNLENS_CACHE_PATH=/tmp/learnlens_ai_cache.sqlite3` for a best-effort per-instance cache. Use Supabase for durable state.
- See `../docs/DEPLOY_VERCEL.md` for the exact step-by-step setup.
