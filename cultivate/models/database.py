"""Database engine, session, and initialization."""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker, declarative_base

from config import SQLALCHEMY_DATABASE_URI, DATA_DIR

engine = create_engine(SQLALCHEMY_DATABASE_URI, echo=False)
db_session = scoped_session(sessionmaker(bind=engine))

Base = declarative_base()
Base.query = db_session.query_property()


def init_db():
    """Create all tables if they don't exist."""
    os.makedirs(DATA_DIR, exist_ok=True)
    import models.prospect
    import models.foundation
    import models.contact
    import models.grant_deadline
    import models.outreach
    import models.activity_log
    import models.action_item
    import models.event
    import models.weekly_goal
    import models.yearly_financial
    import models.foundation_grant
    import models.foundation_officer
    import models.research_note
    Base.metadata.create_all(bind=engine)
    migrate_db()


def migrate_db():
    """Add new columns to existing tables (SQLite ALTER TABLE)."""
    import sqlite3
    from config import DB_PATH
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # New deep-research columns on foundation_data
    new_cols = [
        ('mission_overlap_score', 'REAL DEFAULT 0'),
        ('bay_area_grant_pct', 'REAL DEFAULT 0'),
        ('giving_trend', 'TEXT'),
        ('years_of_data', 'INTEGER DEFAULT 0'),
        ('deep_research_at', 'TEXT'),
    ]
    for col_name, col_type in new_cols:
        try:
            cursor.execute(f'ALTER TABLE foundation_data ADD COLUMN {col_name} {col_type}')
        except sqlite3.OperationalError:
            pass  # column already exists
    conn.commit()
    conn.close()
