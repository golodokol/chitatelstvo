-- Миграция: таблица enrollments (запись на модуль)
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
