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
    import models.volunteer
    import models.shift
    import models.signup
    import models.recurring_series
    import models.activity_log
    import models.sms_code
    import models.staff
    Base.metadata.create_all(bind=engine)

    # Migrate: add new columns to existing DBs
    from sqlalchemy import text, inspect
    insp = inspect(engine)
    existing_cols = {c['name'] for c in insp.get_columns('volunteers')}
    for col, coldef in [
        ('preferred_shift_types', "TEXT DEFAULT '[]'"),
        ('photo', 'VARCHAR(200)'),
        ('is_youth', 'BOOLEAN DEFAULT 0'),
        ('last_seen', 'DATETIME'),
    ]:
        if col not in existing_cols:
            with engine.begin() as conn:
                conn.execute(text(f'ALTER TABLE volunteers ADD COLUMN {col} {coldef}'))
