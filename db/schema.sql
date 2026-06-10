-- Литературная школа онлайн — схема PostgreSQL (масштаб до 1000+ семей)

CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TABLE IF NOT EXISTS families (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    parent_name     TEXT NOT NULL,
    parent_email    TEXT NOT NULL,
    parent_telegram TEXT,
    telegram_chat_id BIGINT,
    notification_channel TEXT NOT NULL DEFAULT 'email'
        CHECK (notification_channel IN ('email', 'telegram', 'both', 'web')),
    progress_token  TEXT NOT NULL UNIQUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_families_email ON families (parent_email);
CREATE INDEX IF NOT EXISTS idx_families_progress_token ON families (progress_token);

CREATE TABLE IF NOT EXISTS children (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    family_id       UUID NOT NULL REFERENCES families(id) ON DELETE CASCADE,
    name            TEXT NOT NULL,
    age             SMALLINT,
    current_level   TEXT NOT NULL DEFAULT 'Старт',
    total_points    INTEGER NOT NULL DEFAULT 0,
    streak_count    INTEGER NOT NULL DEFAULT 0,
    module_week     SMALLINT NOT NULL DEFAULT 1,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_children_family ON children (family_id);
CREATE INDEX IF NOT EXISTS idx_children_name ON children (name);

CREATE TABLE IF NOT EXISTS child_badges (
    child_id    UUID NOT NULL REFERENCES children(id) ON DELETE CASCADE,
    badge_name  TEXT NOT NULL,
    earned_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (child_id, badge_name)
);

CREATE TABLE IF NOT EXISTS events (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    idempotency_key  TEXT NOT NULL UNIQUE,
    child_id         UUID NOT NULL REFERENCES children(id) ON DELETE CASCADE,
    event_type       TEXT NOT NULL,
    tale_title       TEXT,
    lesson_date      DATE,
    notes            TEXT,
    payload          JSONB,
    status           TEXT NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending', 'processing', 'done', 'failed')),
    error_message    TEXT,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    processed_at     TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_events_child ON events (child_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_events_status ON events (status);

CREATE TABLE IF NOT EXISTS rewards (
    event_id        UUID PRIMARY KEY REFERENCES events(id) ON DELETE CASCADE,
    reward_type     TEXT,
    points          INTEGER NOT NULL DEFAULT 0,
    badge_name      TEXT,
    level_change    TEXT,
    child_message   TEXT NOT NULL,
    parent_message  TEXT NOT NULL,
    next_action     TEXT NOT NULL,
    source          TEXT NOT NULL DEFAULT 'rules'
);

CREATE TABLE IF NOT EXISTS parent_notifications (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    family_id   UUID NOT NULL REFERENCES families(id) ON DELETE CASCADE,
    child_id    UUID NOT NULL REFERENCES children(id) ON DELETE CASCADE,
    event_id    UUID REFERENCES events(id) ON DELETE SET NULL,
    channel     TEXT NOT NULL CHECK (channel IN ('email', 'telegram', 'web')),
    status      TEXT NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending', 'sent', 'failed', 'stored')),
    message     TEXT NOT NULL,
    error_message TEXT,
    sent_at     TIMESTAMPTZ,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_notifications_family ON parent_notifications (family_id, created_at DESC);
