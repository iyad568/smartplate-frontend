-- SmartPlate Auth — in-place upgrade for existing databases.
--
-- Apply this if you ALREADY have a `users` table from the old (pre-OTP+RBAC)
-- schema and want to bring it forward without dropping data.
--
--    psql "$DATABASE_URL" -f schema_upgrade.sql
--
-- Idempotent: safe to run more than once.

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

-- ─── users — add the new role column if missing ────────────────────────────

ALTER TABLE users
    ADD COLUMN IF NOT EXISTS role user_role NOT NULL DEFAULT 'user';

CREATE INDEX IF NOT EXISTS ix_users_role ON users (role);

-- Make phone & hashed_password NOT NULL again (was made nullable by the
-- old Google-OAuth migration). Backfill any NULLs to safe defaults so the
-- ALTER doesn't fail on existing rows.
UPDATE users SET phone = '' WHERE phone IS NULL;
UPDATE users SET hashed_password = '' WHERE hashed_password IS NULL;

ALTER TABLE users
    ALTER COLUMN phone           SET NOT NULL,
    ALTER COLUMN hashed_password SET NOT NULL;

-- ─── otp_codes — create if missing ─────────────────────────────────────────

CREATE TABLE IF NOT EXISTS otp_codes (
    id          VARCHAR(36) PRIMARY KEY,
    user_id     VARCHAR(36)  NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    code        VARCHAR(255) NOT NULL,
    purpose     otp_purpose  NOT NULL DEFAULT 'signup',
    expires_at  TIMESTAMPTZ  NOT NULL,
    used        BOOLEAN      NOT NULL DEFAULT FALSE,
    created_at  TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_otp_user_id           ON otp_codes (user_id);
CREATE INDEX IF NOT EXISTS ix_otp_user_purpose_used ON otp_codes (user_id, purpose, used);

-- ─── verification_codes — drop the legacy table if present ─────────────────
DROP TABLE IF EXISTS verification_codes;

COMMIT;
