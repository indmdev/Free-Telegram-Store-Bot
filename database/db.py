"""Database connection and session management."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from contextlib import contextmanager
from config.settings import settings
from database.models import Base

# Create database engine
engine = create_engine(settings.DATABASE_URL, echo=False)

# Create session factory
SessionFactory = sessionmaker(bind=engine)
Session = scoped_session(SessionFactory)


def init_db():
    """Initialize the database by creating all tables."""
    Base.metadata.create_all(engine)
    print("[OK] Database tables created successfully")


@contextmanager
def get_db_session():
    """Provide a transactional scope for database operations."""
    session = Session()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()
