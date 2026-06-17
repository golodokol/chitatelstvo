-- Награды из сундука: одна запись на ребёнка + сказку (неделю)

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
