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
    birth_date      DATE,
    birthday_gift_year SMALLINT,
    bonus_unlock_weeks SMALLINT NOT NULL DEFAULT 0,
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

CREATE TABLE IF NOT EXISTS enrollments (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    child_id            UUID NOT NULL REFERENCES children(id) ON DELETE CASCADE,
    module_id           SMALLINT NOT NULL,
    status              TEXT NOT NULL DEFAULT 'active'
        CHECK (status IN ('active', 'paused', 'completed')),
    start_date          DATE,
    chosen_stage        TEXT,
    chosen_tale_number  SMALLINT,
    chosen_tale_slug    TEXT,
    chosen_tale_title   TEXT,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_enrollments_child ON enrollments (child_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_enrollments_module ON enrollments (module_id);

CREATE TABLE IF NOT EXISTS tale_ratings (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    child_id    UUID NOT NULL REFERENCES children(id) ON DELETE CASCADE,
    tale_slug   TEXT NOT NULL,
    tale_title  TEXT,
    rating      SMALLINT NOT NULL CHECK (rating BETWEEN 1 AND 10),
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (child_id, tale_slug)
);

CREATE INDEX IF NOT EXISTS idx_tale_ratings_child ON tale_ratings (child_id, rating DESC, updated_at DESC);

CREATE TABLE IF NOT EXISTS chest_claims (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    child_id        UUID NOT NULL REFERENCES children(id) ON DELETE CASCADE,
    tale_slug       TEXT NOT NULL,
    tale_title      TEXT,
    module_week     SMALLINT,
    items           JSONB NOT NULL DEFAULT '[]'::jsonb,
    claimed_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (child_id, tale_slug)
);

CREATE INDEX IF NOT EXISTS idx_chest_claims_child ON chest_claims (child_id, claimed_at DESC);

-- Мини-кабинет Читательской экспедиции (отдельно от LMS-кабинета школы)

CREATE TABLE IF NOT EXISTS expedition_profiles (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    child_id    UUID NOT NULL UNIQUE REFERENCES children(id) ON DELETE CASCADE,
    family_id   UUID NOT NULL REFERENCES families(id) ON DELETE CASCADE,
    nickname    TEXT,
    avatar      TEXT NOT NULL DEFAULT 'compass',
    started_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    level       TEXT NOT NULL DEFAULT 'Старт',
    payload     JSONB
);

CREATE TABLE IF NOT EXISTS expedition_passports (
    profile_id      UUID PRIMARY KEY REFERENCES expedition_profiles(id) ON DELETE CASCADE,
    favorite_story  TEXT,
    favorite_hero   TEXT,
    last_work       TEXT,
    next_stop       TEXT,
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS expedition_story_progress (
    child_id     UUID NOT NULL REFERENCES children(id) ON DELETE CASCADE,
    story_slug   TEXT NOT NULL,
    status       TEXT NOT NULL DEFAULT 'open',
    creative     TEXT,
    completed_at TIMESTAMPTZ,
    payload      JSONB,
    PRIMARY KEY (child_id, story_slug)
);

CREATE TABLE IF NOT EXISTS expedition_region_stamps (
    child_id      UUID NOT NULL REFERENCES children(id) ON DELETE CASCADE,
    region_slug   TEXT NOT NULL,
    stamp_level   TEXT NOT NULL DEFAULT 'marker'
        CHECK (stamp_level IN ('marker', 'basic', 'gold')),
    poetic_title  TEXT,
    earned_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (child_id, region_slug)
);

CREATE TABLE IF NOT EXISTS expedition_tariffs (
    id              TEXT PRIMARY KEY,
    code            TEXT NOT NULL UNIQUE,
    title           TEXT NOT NULL,
    blurb           TEXT,
    price_rub       INTEGER,
    period_days     INTEGER,
    child_profiles  SMALLINT NOT NULL DEFAULT 1,
    features        JSONB,
    audience        TEXT NOT NULL DEFAULT 'parent',
    active          BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS expedition_purchases (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    family_id   UUID NOT NULL REFERENCES families(id) ON DELETE CASCADE,
    tariff_id   TEXT NOT NULL,
    status      TEXT NOT NULL DEFAULT 'pending',
    payload     JSONB,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS expedition_user_badges (
    child_id     UUID NOT NULL REFERENCES children(id) ON DELETE CASCADE,
    badge_id     TEXT NOT NULL,
    earned_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (child_id, badge_id)
);

CREATE TABLE IF NOT EXISTS expedition_route_progress (
    child_id     UUID NOT NULL REFERENCES children(id) ON DELETE CASCADE,
    route_slug   TEXT NOT NULL,
    step_index   SMALLINT NOT NULL DEFAULT 0,
    status       TEXT NOT NULL DEFAULT 'open',
    updated_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (child_id, route_slug)
);

CREATE TABLE IF NOT EXISTS expedition_task_attempts (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    child_id     UUID NOT NULL REFERENCES children(id) ON DELETE CASCADE,
    story_slug   TEXT NOT NULL,
    option_id    TEXT,
    ok           BOOLEAN,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS expedition_subscriptions (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    family_id    UUID NOT NULL REFERENCES families(id) ON DELETE CASCADE,
    tariff_id    TEXT NOT NULL,
    status       TEXT NOT NULL DEFAULT 'active',
    starts_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    ends_at      TIMESTAMPTZ,
    payload      JSONB
);

CREATE TABLE IF NOT EXISTS expedition_library_partners (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org          TEXT NOT NULL,
    city         TEXT,
    region       TEXT,
    contact      TEXT,
    email        TEXT,
    status       TEXT NOT NULL DEFAULT 'new',
    payload      JSONB,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS expedition_library_events (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    partner_id   UUID REFERENCES expedition_library_partners(id) ON DELETE SET NULL,
    title        TEXT NOT NULL,
    event_date   DATE,
    payload      JSONB,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS expedition_library_qr (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    partner_id   UUID REFERENCES expedition_library_partners(id) ON DELETE CASCADE,
    code         TEXT NOT NULL UNIQUE,
    target_url   TEXT,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_expedition_profiles_family ON expedition_profiles (family_id);
CREATE INDEX IF NOT EXISTS idx_expedition_purchases_family ON expedition_purchases (family_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_expedition_subscriptions_family ON expedition_subscriptions (family_id, status);
