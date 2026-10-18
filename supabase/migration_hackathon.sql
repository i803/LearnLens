-- Run once in Supabase SQL Editor for the LearnLens hackathon upgrades.
-- Browser clients must never use the service/secret key.
create table if not exists classes (
  code text primary key,
  name text not null,
  teacher_name text not null default 'Teacher',
  teacher_key_hash text not null,
  synthetic boolean not null default false,
  created_at timestamptz not null default now()
);

alter table students add column if not exists class_code text references classes(code);
alter table students add column if not exists language text not null default 'en';
alter table students add column if not exists consented_at timestamptz;
alter table students add column if not exists synthetic boolean not null default false;

alter table mastery add column if not exists p_known numeric not null default 0.3;
alter table mastery add column if not exists last_practiced timestamptz;
alter table mastery add column if not exists next_due timestamptz;
alter table mastery add column if not exists confirmed boolean not null default false;
alter table diagnostics add column if not exists misconception_tag text;
alter table diagnostics add column if not exists provider text;
alter table work_items add column if not exists misconception_tag text;

create table if not exists ai_cache (
  key text primary key,
  kind text not null,
  payload jsonb not null,
  created_at timestamptz not null default now()
);

-- Service-side access only; do not add anon/authenticated SELECT policies.
alter table students enable row level security;
alter table attempts enable row level security;
alter table mastery enable row level security;
alter table diagnostics enable row level security;
alter table work_items enable row level security;
alter table classes enable row level security;
alter table ai_cache enable row level security;
alter table feedback enable row level security;
alter table uploads enable row level security;
alter table diagnostic_questions enable row level security;
alter table mastery_snapshots enable row level security;
