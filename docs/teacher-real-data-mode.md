# Teacher pages: real-data and local-demo behavior

The `/teacher` and `/teacher/analytics` pages never use a seeded student roster in a configured or hosted environment. A blank real classroom is expected until students join and produce saved learning activity.

## Mode rules

| Environment | Synthetic `CSE-A` | Teacher classroom source |
|---|---|---|
| Clean local clone, no `.env` files and no service credentials | Enabled as a clearly labelled judge/demo fixture | Local-only synthetic fixture; newly created real classes can also be tested |
| Local checkout with any project `.env`/`.env.local` file or Supabase/AI credentials | Disabled, even if the file is incomplete | Real classes and student events only; without Supabase, state is in memory and lost on backend restart |
| Vercel Preview/Production or another detected hosted environment | Always disabled | Supabase-backed real classes only; classroom creation/joining/heatmap access fail closed if persistent storage is not configured or reachable |

`.env.example` files are templates and do not disable the clean-checkout demo by themselves. Never commit a real `.env` file or secret.

## Hosted setup

1. Create a Supabase project and run `supabase/schema.sql` for a fresh database, or review the applicable migration before updating an existing database.
2. Configure `SUPABASE_URL` and `SUPABASE_SECRET_KEY` as server-side backend environment variables in Vercel. Do not put the secret in a `NEXT_PUBLIC_` variable.
3. Set the frontend's `AI_SERVICE_URL` to the backend URL. Set allowed origins on the backend as documented in `DEPLOY_VERCEL.md`.
4. Redeploy, check `/health` for Supabase configuration/availability, then test a fresh class.
5. On `/teacher`, create a class and securely save the one-time teacher key. Open `/join` in a separate browser, enter that class code, choose a nickname, and explicitly consent. Complete learning actions to create real records. Only that class's authorized teacher should see them.
6. Open `/teacher/classes/CSE-A/heatmap` without credentials, then with `demo-teacher-key`, as a negative test. On the hosted deployment both attempts must fail without returning a synthetic roster.

## Security and interpretation

- The general `/teacher/analytics` endpoint without a class code returns mode/persistence metadata only, not aggregate student statistics. Class analytics require a class code and matching `X-Teacher-Key`.
- Student rows are scoped to the authorized class, and synthetic student rows are filtered out of real-data paths.
- The teacher key is shown once on class creation; the server stores a hash. Share the key only with the teacher and do not put it in a URL or public issue.
- Misconception counts and mastery estimates describe saved prototype activity. They are not independently validated learning outcomes or grades.
