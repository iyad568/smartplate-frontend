-- SmartPlate Auth — PostgreSQL schema
--
-- Hand-written reference matching what the SQLAlchemy models in app/models/
-- produce. In production prefer:
--     alembic revision --autogenerate -m "init"
--     alembic upgrade head
--
-- Compatible with PostgreSQL 14+.

BEGIN;

-- ─── Enums ──────────────────────────────────────────────────────────────────

DO $$ BEGIN
    CREATE TYPE user_role AS ENUM ('user', 'sos', 'depanage', 'admin');
EXCEPTION
    WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
    CREATE TYPE otp_purpose AS ENUM ('signup', 'login');
EXCEPTION
    WHEN duplicate_object THEN NULL;
END $$;

-- ─── users ─────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS users (
    id              VARCHAR(36) PRIMARY KEY,
    full_name       VARCHAR(120)          NOT NULL,
    email           VARCHAR(255)          NOT NULL UNIQUE,
    phone           VARCHAR(30)           NOT NULL,
    hashed_password VARCHAR(255)          NOT NULL,
    role            user_role             NOT NULL DEFAULT 'user',
    is_verified     BOOLEAN               NOT NULL DEFAULT FALSE,
    -- Carryover columns from the OAuth-era schema (kept for backward compat).
    provider        VARCHAR(50)           NOT NULL DEFAULT 'email',
    google_id       VARCHAR(255),
    profile_picture VARCHAR(500),
    created_at      TIMESTAMPTZ           NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ           NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_users_email ON users (email);
CREATE INDEX IF NOT EXISTS ix_users_role  ON users (role);

-- ─── otp_codes ─────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS otp_codes (
    id          VARCHAR(36) PRIMARY KEY,
    user_id     VARCHAR(36)  NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    code        VARCHAR(255) NOT NULL,           -- bcrypt hash of the 6-digit OTP
    purpose     otp_purpose  NOT NULL DEFAULT 'signup',
    expires_at  TIMESTAMPTZ  NOT NULL,
    used        BOOLEAN      NOT NULL DEFAULT FALSE,
    created_at  TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_otp_user_id            ON otp_codes (user_id);
CREATE INDEX IF NOT EXISTS ix_otp_user_purpose_used  ON otp_codes (user_id, purpose, used);

-- ─── Optional: auto-update users.updated_at on row change ──────────────────

CREATE OR REPLACE FUNCTION trg_set_updated_at() RETURNS trigger AS $$
BEGIN
    NEW.updated_at := NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS users_set_updated_at ON users;
CREATE TRIGGER users_set_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION trg_set_updated_at();

COMMIT;

-- ─── Manually grant admin to a user ────────────────────────────────────────
-- UPDATE users SET role = 'admin' WHERE email = 'someone@gmail.com';
