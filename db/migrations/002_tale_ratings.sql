-- Оценки сказок (1–10) для читательского дневника
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
