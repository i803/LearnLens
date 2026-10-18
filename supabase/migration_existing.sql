-- Run this AFTER your original LearnLens schema when the database already exists.
-- It is safe to run more than once.

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
  marks_obtained numeric,
  marks_total numeric,
  concept_id text references concepts(id),
  error_type text,
  ai_confidence numeric,
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


alter table work_items add column if not exists correct_answer text;
alter table work_items add column if not exists grading_confidence numeric default 0;

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
create index if not exists feedback_created_idx on feedback(created_at desc);
