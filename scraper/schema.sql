-- Supabase / Postgres schema for HaiDoIT job data
-- Run once: psql $DATABASE_URL -f schema.sql

CREATE TABLE IF NOT EXISTS jobs (
    job_url     TEXT PRIMARY KEY,
    site        TEXT NOT NULL,
    job_id      TEXT,
    title       TEXT,
    company     TEXT,
    location    TEXT,
    salary      TEXT,
    experience_level TEXT,
    job_level   TEXT,
    employment_type  TEXT,
    work_model  TEXT,
    skills      JSONB DEFAULT '[]',
    description TEXT,
    description_consolidated TEXT,
    date_posted TEXT,
    valid_through TEXT,

    -- step-05 extracted (Claude)
    title_cleaned TEXT,
    tech_stack    JSONB DEFAULT '[]',
    keywords      JSONB DEFAULT '[]',

    -- step-06 classified (Jev)
    title_category    TEXT,
    seniority_category TEXT,
    location_category  TEXT,
    work_model_category TEXT,

    -- metadata
    first_seen_at TIMESTAMPTZ DEFAULT now(),
    updated_at    TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_jobs_site ON jobs (site);
CREATE INDEX IF NOT EXISTS idx_jobs_title_category ON jobs (title_category);
CREATE INDEX IF NOT EXISTS idx_jobs_seniority ON jobs (seniority_category);
CREATE INDEX IF NOT EXISTS idx_jobs_location ON jobs (location_category);
CREATE INDEX IF NOT EXISTS idx_jobs_date_posted ON jobs (date_posted);
