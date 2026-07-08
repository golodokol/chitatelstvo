-- Дата рождения ребёнка и подарок на день рождения (1 доп. урок в год)
ALTER TABLE children
    ADD COLUMN IF NOT EXISTS birth_date DATE,
    ADD COLUMN IF NOT EXISTS birthday_gift_year SMALLINT,
    ADD COLUMN IF NOT EXISTS bonus_unlock_weeks SMALLINT NOT NULL DEFAULT 0;
