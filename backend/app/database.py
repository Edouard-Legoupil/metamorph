"""
Database Configuration and Setup

Handles SQL database connections and session management.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.ext.declarative import declarative_base
import os

# SQL database configuration
SQLALCHEMY_DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/metamorph"
)

# Create SQL engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True,
    pool_recycle=3600,
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base for models
Base = declarative_base()


def get_db():
    """
    Dependency to get database session.
    
    Usage:
        from fastapi import Depends
        from app.database import get_db
        
        def some_route(db: Session = Depends(get_db)):
            # Use db here
            pass
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize database tables.
    
    Creates all tables defined in the models.
    """
    from app.models.sql.base import Base
    from app.models.sql.website import (
        Website, DiscoveredFile, ScrapeSession, IngestionJob, WebsiteTopic
    )
    from app.models.sql.user import User, Team, TeamMember
    from app.models.sql.settings import (
        Topic, AppSettings, CrawlerSettings, NotificationSettings
    )
    
    # Import all models to ensure they're registered with Base
    # SQLAlchemy will create tables for all models that inherit from Base
    
    # Import to trigger model registration
    # All models are imported above, which registers them with SQLAlchemy's Base
    
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")


def drop_db():
    """
    Drop all database tables.
    
    WARNING: This will delete all data!
    """
    from app.models.sql.base import Base
    print("Dropping database tables...")
    Base.metadata.drop_all(bind=engine)
    print("Database tables dropped successfully!")


# For backwards compatibility
BaseModel = declarative_base()
