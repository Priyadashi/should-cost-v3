"""Lightweight startup migrations for additive schema changes."""
from sqlalchemy import text, inspect


def run_migrations(engine):
    """Add missing columns to existing tables. Safe to run multiple times."""
    dialect = engine.dialect.name
    inspector = inspect(engine)

    def _has_column(table, column):
        cols = [c["name"] for c in inspector.get_columns(table)]
        return column in cols

    def _add_column(conn, table, column, col_type):
        if not _has_column(table, column):
            conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {column} {col_type}"))

    with engine.connect() as conn:
        # process_templates: columns added in v2
        _add_column(conn, "process_templates", "default_batch_size", "INTEGER DEFAULT 100")
        _add_column(conn, "process_templates", "default_operators", "INTEGER DEFAULT 1")
        _add_column(conn, "process_templates", "default_tooling_cost_per_unit", "FLOAT DEFAULT 0")
        # cost_sheets: columns added in v2
        _add_column(conn, "cost_sheets", "supplier_name", "VARCHAR(200)")
        conn.commit()
