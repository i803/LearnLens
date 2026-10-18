-- LearnLens AI -- Supabase schema
-- Full schema: run this in the Supabase SQL Editor for a fresh database,
-- OR use the migration file below if your original LearnLens tables already exist.

create extension if not exists vector;
create extension if not exists pgcrypto;

create table if not exists classes (
  code text primary key,
  name text not null,
  teacher_name text not null default 'Teacher',
  teacher_key_hash text not null,
  synthetic boolean not null default false,
  created_at timestamptz not null default now()
);

create table if not exists students (
  id text primary key,
  display_name text not null,
  class_code text references classes(code),
  language text not null default 'en',
  consented_at timestamptz,
  synthetic boolean not null default false,
  created_at timestamptz not null default now()
);

create table if not exists concepts (
  id text primary key,
  subject text not null,
  topic text not null,
  name text not null,
  metadata jsonb not null default '{}'::jsonb
);

create table if not exists source_chunks (
  id text primary key,
  concept_id text references concepts(id),
  title text not null,
  url text,
  content text not null,
  embedding vector(768)
);

create index if not exists source_chunks_embedding_idx
  on source_chunks using ivfflat (embedding vector_cosine_ops) with (lists = 50);

create table if not exists diagnostics (
  id uuid primary key default gen_random_uuid(),
  student_id text references students(id),
  weakest_concept_id text references concepts(id),
  confidence numeric,
  evidence jsonb not null default '[]'::jsonb,
  diagnosis text,
  recommendation text,
  misconception_tag text,
  provider text,
  used_fallback boolean not null default false,
  created_at timestamptz not null default now()
);

create table if not exists attempts (
  id uuid primary key default gen_random_uuid(),
  student_id text references students(id),
  concept_id text references concepts(id),
  question_id text,
  difficulty text,
  correct boolean not null,
  mastery_before numeric not null,
  mastery_after numeric not null,
  student_answer text,
  expected_answer text,
  session_id uuid,
  created_at timestamptz not null default now()
);

create table if not exists mastery (
  student_id text references students(id),
  concept_id text references concepts(id),
  mastery numeric not null default 0,
  attempts int not null default 0,
  p_known numeric not null default 0.3,
  last_practiced timestamptz,
  next_due timestamptz,
  confirmed boolean not null default false,
  updated_at timestamptz not null default now(),
  primary key (student_id, concept_id)
);

create table if not exists uploads (
  id uuid primary key default gen_random_uuid(),
  student_id text references students(id),
  filename text not null,
  file_type text,
  source_text text,
  created_at timestamptz not null default now()
);

create table if not exists work_items (
  id uuid primary key default gen_random_uuid(),
  upload_id uuid references uploads(id) on delete cascade,
  student_id text references students(id),
  question_number text,
  question_text text not null,
  student_answer text,
  correct_answer text,
  marks_obtained numeric,
  marks_total numeric,
  concept_id text references concepts(id),
  error_type text,
  misconception_tag text,
  ai_confidence numeric,
  grading_confidence numeric default 0,
  created_at timestamptz not null default now()
);

create table if not exists diagnostic_questions (
  id uuid primary key default gen_random_uuid(),
  student_id text references students(id),
  diagnostic_id uuid references diagnostics(id) on delete cascade,
  concept_id text references concepts(id),
  question_id text not null,
  question_text text not null,
  options jsonb,
  correct_answer text not null,
  explanation text,
  difficulty text,
  source_context jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  unique (student_id, question_id)
);

create table if not exists learning_sessions (
  id uuid primary key default gen_random_uuid(),
  student_id text references students(id),
  concept_id text references concepts(id),
  starting_mastery numeric,
  ending_mastery numeric,
  status text not null default 'active',
  created_at timestamptz not null default now(),
  completed_at timestamptz
);

create table if not exists mastery_snapshots (
  id uuid primary key default gen_random_uuid(),
  student_id text references students(id),
  concept_id text references concepts(id),
  previous_mastery numeric not null,
  new_mastery numeric not null,
  reason text,
  source text,
  session_id uuid references learning_sessions(id),
  created_at timestamptz not null default now()
);

-- Backward-compatible upgrades for an existing attempts table.
alter table attempts add column if not exists student_answer text;
alter table attempts add column if not exists expected_answer text;
alter table attempts add column if not exists session_id uuid references learning_sessions(id);

create index if not exists uploads_student_idx on uploads(student_id);
create index if not exists work_items_student_idx on work_items(student_id);
create index if not exists work_items_concept_idx on work_items(concept_id);
create index if not exists diagnostic_questions_student_idx on diagnostic_questions(student_id);
create index if not exists diagnostic_questions_diagnostic_idx on diagnostic_questions(diagnostic_id);
create index if not exists learning_sessions_student_idx on learning_sessions(student_id);
create index if not exists learning_sessions_concept_idx on learning_sessions(concept_id);
create index if not exists mastery_snapshots_student_idx on mastery_snapshots(student_id);
create index if not exists mastery_snapshots_concept_idx on mastery_snapshots(concept_id);

create or replace function match_source_chunks(
  query_embedding vector(768),
  match_concept_id text,
  match_count int default 3
)
returns table (id text, title text, content text, similarity float)
language sql stable
as $$
  select id, title, content,
         1 - (embedding <=> query_embedding) as similarity
  from source_chunks
  where concept_id = match_concept_id
  order by embedding <=> query_embedding
  limit match_count;
$$;

-- Student feedback (optional post-session survey)
create table if not exists feedback (
  id uuid primary key default gen_random_uuid(),
  student_id text references students(id),
  session_id uuid references learning_sessions(id),
  rating int not null check (rating between 1 and 5),
  helpful_aspects jsonb not null default '[]'::jsonb,
  confusing_aspects jsonb not null default '[]'::jsonb,
  would_use_again text check (would_use_again in ('yes','maybe','no')),
  comment text,
  created_at timestamptz not null default now()
);
create index if not exists feedback_created_idx on feedback(created_at desc);


create table if not exists ai_cache (
  key text primary key,
  kind text not null,
  payload jsonb not null,
  created_at timestamptz not null default now()
);

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
