-- Blockchain-Based Academic Database Management System
-- Run this in Supabase SQL Editor.

create extension if not exists pgcrypto;

create table if not exists profiles (
    id uuid primary key references auth.users(id) on delete cascade,
    name text not null,
    email text unique not null,
    role text not null check (role in ('student','faculty','admin')),
    department text,
    created_at timestamptz default now()
);

create table if not exists courses (
    id uuid primary key default gen_random_uuid(),
    code text unique not null,
    name text not null,
    credits integer not null check (credits > 0),
    department text,
    created_at timestamptz default now()
);

create table if not exists academic_records (
    id uuid primary key default gen_random_uuid(),
    student_id uuid not null references profiles(id) on delete cascade,
    course_id uuid not null references courses(id) on delete restrict,
    semester text not null,
    academic_year text not null,
    marks integer not null check (marks between 0 and 100),
    attendance numeric(5,2) not null check (attendance between 0 and 100),
    grade text not null,
    updated_by uuid references profiles(id),
    created_at timestamptz default now(),
    updated_at timestamptz default now()
);

create table if not exists authority_nodes (
    node_id uuid primary key default gen_random_uuid(),
    user_id uuid unique not null references profiles(id) on delete cascade,
    role text not null,
    public_key text not null,
    status text not null default 'ACTIVE' check (status in ('ACTIVE','REVOKED')),
    created_at timestamptz default now()
);

create table if not exists blocks (
    block_number integer primary key,
    timestamp timestamptz not null,
    previous_hash text not null,
    transaction_hash text not null,
    transaction_data jsonb not null,
    validator_id uuid,
    signature text not null,
    block_hash text not null unique
);

create index if not exists idx_records_student on academic_records(student_id);
create index if not exists idx_records_course on academic_records(course_id);
create index if not exists idx_blocks_validator on blocks(validator_id);

-- Demo course data:
insert into courses (code, name, credits, department)
values
('CS101', 'Programming Fundamentals', 4, 'CSE'),
('EE201', 'Electrical Machines', 4, 'EEE'),
('EE202', 'Power Systems', 4, 'EEE'),
('CS301', 'Network Security', 3, 'CSE')
on conflict (code) do nothing;

-- For a classroom demo, you may disable email confirmation:
-- Supabase Dashboard -> Authentication -> Providers -> Email -> Confirm email OFF
--
-- IMPORTANT:
-- This MVP uses the Supabase publishable/anon key on the server and relies on
-- Supabase Auth for passwords. Never put a service-role key in frontend code.
