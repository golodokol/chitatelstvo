-- Читательская экспедиция: заявки библиотек и легенды на модерацию

CREATE TABLE IF NOT EXISTS expedition_submissions (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    kind            TEXT NOT NULL CHECK (kind IN ('library', 'legend', 'error')),
    status          TEXT NOT NULL DEFAULT 'submitted'
        CHECK (status IN (
            'draft',
            'submitted',
            'needs_info',
            'editorial_review',
            'library_confirmed',
            'expert_review',
            'published_tradition',
            'unpublished'
        )),
    payload         JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_expedition_submissions_kind ON expedition_submissions (kind, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_expedition_submissions_status ON expedition_submissions (status);
