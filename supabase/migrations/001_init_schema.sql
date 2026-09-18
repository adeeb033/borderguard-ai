-- BorderGuard AI schema for Supabase Postgres
-- Run this in the Supabase SQL editor or via CLI migration tool.

create extension if not exists "pgcrypto";

create table if not exists public.reference_documents (
    id bigserial primary key,
    document_type text,
    document_number text not null unique,
    full_name text,
    date_of_birth text,
    nationality text,
    expiry_date text,
    gender text,
    status text default 'ACTIVE',
    created_at timestamptz default now()
);

create table if not exists public.checkpoint_gates (
    id serial primary key,
    gate_code text not null unique,
    status text default 'ACTIVE',
    created_at timestamptz default now()
);

create table if not exists public.screening_history (
    id bigserial primary key,
    screening_id text not null unique,
    filename text,
    applicant_name text,
    document_type text,
    risk_score numeric(5,2),
    risk_level text,
    status text default 'PENDING',
    review_status text default 'PENDING',
    officer_notes text,
    reviewed_at timestamptz,
    ocr_confidence numeric(5,2),
    validation_score numeric(5,2),
    tampering_score numeric(5,2),
    face_detected boolean default false,
    risk_reasons jsonb default '[]'::jsonb,
    screening_date timestamptz default now()
);

create table if not exists public.security_alerts (
    id bigserial primary key,
    alert_id text not null unique,
    screening_id text not null,
    filename text,
    applicant_name text,
    document_type text,
    risk_score numeric(5,2),
    risk_level text,
    alert_type text,
    description text,
    status text default 'OPEN',
    created_at timestamptz default now()
);

create index if not exists idx_reference_documents_number
    on public.reference_documents (document_number);

create index if not exists idx_screening_history_screening_id
    on public.screening_history (screening_id);

create index if not exists idx_screening_history_date
    on public.screening_history (screening_date desc);

create index if not exists idx_security_alerts_screening_id
    on public.security_alerts (screening_id);
