from __future__ import annotations

from sqlalchemy import create_engine, inspect, text


def _is_sqlite(database_url: str) -> bool:
    return database_url.startswith("sqlite:")


def _ensure_sqlite_column(engine, table: str, column_name: str, column_type: str) -> None:
    inspector = inspect(engine)
    columns = [c["name"] for c in inspector.get_columns(table)]
    if column_name in columns:
        return
    # SQLite supports adding nullable columns with ALTER TABLE.
    with engine.begin() as conn:
        conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {column_name} {column_type}"))


def run_migrations(database_url: str) -> None:
    engine = create_engine(database_url, future=True)
    try:
        if _is_sqlite(database_url):
            # Ensure auth-related columns exist on an upgraded DB.
            _ensure_sqlite_column(engine, "users", "email", "TEXT")
            _ensure_sqlite_column(engine, "users", "password_hash", "TEXT")
            _ensure_sqlite_column(engine, "users", "role", "TEXT")
            _ensure_sqlite_column(engine, "users", "whatsapp_number", "TEXT")
    finally:
        engine.dispose()
