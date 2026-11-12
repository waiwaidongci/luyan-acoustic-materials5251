"""Idempotent lightweight schema guard for the recalculation columns (migration 002).

The project convention is create_all for missing tables plus reviewed DDL in migrations/.
An existing decision_runs table predating migration 002 would miss the provenance/lineage
columns; adding them on startup keeps upgraded environments working without a manual step.
"""
from sqlalchemy import inspect, text

_REQUIRED = {
    'source_fingerprint': "VARCHAR(64) NOT NULL DEFAULT ''",
    'source_signature': 'JSON NULL',
    'recalc_of_id': 'INTEGER NULL',
    'recalc_seq': 'INTEGER NOT NULL DEFAULT 0',
    'recalc_status': "VARCHAR(20) NOT NULL DEFAULT ''",
}


def ensure_run_columns(engine):
    inspector = inspect(engine)
    if 'decision_runs' not in inspector.get_table_names():
        return
    existing = {c['name'] for c in inspector.get_columns('decision_runs')}
    dialect = engine.dialect.name
    type_sql = 'JSON'
    with engine.begin() as conn:
        for name, ddl in _REQUIRED.items():
            if name in existing:
                continue
            if name == 'source_signature' and dialect == 'sqlite':
                ddl = 'JSON'  # SQLite stores JSON as TEXT; the type name is accepted.
            conn.execute(text(f'ALTER TABLE decision_runs ADD COLUMN {name} {ddl}'))
