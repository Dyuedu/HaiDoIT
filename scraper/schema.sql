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

-- ---------------------------------------------------------------------------
-- Nhip mot: moi tin, moi ngay, mot hang. Mot snapshot la anh chup mot ngay da
-- qua — mat la khong crawl lai duoc. Bang nay la thu khong duoc cat (AD-28).
CREATE TABLE IF NOT EXISTS job_observations (
    job_url       TEXT NOT NULL,
    snapshot_date DATE NOT NULL,
    site          TEXT NOT NULL,
    seen_at       TIMESTAMPTZ DEFAULT now(),
    PRIMARY KEY (job_url, snapshot_date)
);

CREATE INDEX IF NOT EXISTS idx_obs_snapshot ON job_observations (snapshot_date);
CREATE INDEX IF NOT EXISTS idx_obs_site_snapshot ON job_observations (site, snapshot_date);

-- ---------------------------------------------------------------------------
-- Cot cua cong trich xuat (extract_gate.py).
-- skills_raw giu NGUYEN VAN ky nang nhu tin viet, ke ca tieng Viet — FR-6 doi
-- bao cao precision/recall tach rieng cho ky nang viet bang tieng Viet, va
-- khong the do duoc dieu do neu chi luu ban da chuan hoa.
-- model_version va prompt_version: FR-6 bat moi ket qua trich xuat phai truy
-- duoc ve dung model va dung prompt da sinh ra no.
ALTER TABLE jobs ADD COLUMN IF NOT EXISTS skills_raw JSONB DEFAULT '[]';
ALTER TABLE jobs ADD COLUMN IF NOT EXISTS years_experience_min NUMERIC;
ALTER TABLE jobs ADD COLUMN IF NOT EXISTS years_experience_max NUMERIC;
ALTER TABLE jobs ADD COLUMN IF NOT EXISTS is_it_job BOOLEAN;
ALTER TABLE jobs ADD COLUMN IF NOT EXISTS it_confidence NUMERIC;
ALTER TABLE jobs ADD COLUMN IF NOT EXISTS model_version TEXT;
ALTER TABLE jobs ADD COLUMN IF NOT EXISTS prompt_version TEXT;

CREATE INDEX IF NOT EXISTS idx_jobs_is_it ON jobs (is_it_job);
