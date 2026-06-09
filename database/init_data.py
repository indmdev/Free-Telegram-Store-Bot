"""Database initialization script with default data."""

from database.db import get_db_session, init_db
from database.models import Settings


def create_default_settings():
    """Create default settings record if it doesn't exist."""
    with get_db_session() as session:
        settings = session.query(Settings).first()
        if not settings:
            settings = Settings(
                welcome_message="Welcome to our Digital Products Store!\n\nBrowse our collection of premium software keys and digital downloads.",
                support_username="",
                channel_username=""
            )
            session.add(settings)
            print("[OK] Default settings created")
        else:
            print("[OK] Settings already exist")


def initialize_database():
    """Initialize database with tables and default data."""
    print("Initializing database...")
    init_db()
    create_default_settings()
    print("[OK] Database initialization complete")


if __name__ == "__main__":
    initialize_database()
