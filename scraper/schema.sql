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
-- Cot cua cong trich xuat (extract.py).
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

-- ---------------------------------------------------------------------------
-- Moi nguon, moi ngay, mot hang. Tin vang mat khoi mot luot listing_complete = false
-- khong chung minh duoc gi; chi luot quet het listing moi noi duoc tin da bi go.
CREATE TABLE IF NOT EXISTS source_runs (
    source           TEXT NOT NULL,
    snapshot_date    DATE NOT NULL,
    listing_complete BOOLEAN NOT NULL,
    seen_count       INTEGER NOT NULL,
    unresolved_count INTEGER NOT NULL DEFAULT 0,
    error            TEXT,
    finished_at      TIMESTAMPTZ DEFAULT now(),
    PRIMARY KEY (source, snapshot_date)
);

ALTER TABLE source_runs ENABLE ROW LEVEL SECURITY;

-- ---------------------------------------------------------------------------
-- Moi noi dung khac nhau cua mot tin, mot hang. Chi de do JD doi thuong xuyen den
-- dau; chua lam tin nao bi trich xuat lai. Bon nguon chi tai chi tiet mot lan
-- (ITNavi, CareerLink, TopDev, ITviec) khong the hien thay doi o day.
CREATE TABLE IF NOT EXISTS job_content_versions (
    job_url         TEXT NOT NULL,
    content_hash    TEXT NOT NULL,
    site            TEXT NOT NULL,
    first_seen_date DATE NOT NULL,
    PRIMARY KEY (job_url, content_hash)
);

CREATE INDEX IF NOT EXISTS idx_versions_site_date ON job_content_versions (site, first_seen_date);

ALTER TABLE job_content_versions ENABLE ROW LEVEL SECURITY;
