#!/usr/bin/env python3
"""Создаёт таблицы из schema.sql или через SQLAlchemy."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from sqlalchemy import text

from db.models import Base
from db.session import engine


def main() -> None:
    schema_path = ROOT / "db" / "schema.sql"
    if schema_path.exists():
        sql = schema_path.read_text(encoding="utf-8")
        with engine.begin() as conn:
            for stmt in sql.split(";"):
                stmt = stmt.strip()
                if stmt:
                    conn.execute(text(stmt))
        print("Таблицы созданы из db/schema.sql")
    else:
        Base.metadata.create_all(bind=engine)
        print("Таблицы созданы через SQLAlchemy")


if __name__ == "__main__":
    main()
