"""
Database Module for AI Enchanly.

This module handles the database setup, session generation, and base declarations
using SQLAlchemy. The default database engine is configured with SQLite.
"""

import logging
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session

# Configure module-level logger
logger = logging.getLogger("enchanly.database")

# Database URL pointing to a local SQLite database file
DATABASE_URL = "sqlite:///./enchanly.db"

# Create the database engine.
# For SQLite, we set check_same_thread=False to allow FastAPI's multithreaded requests
# to reuse the same database connection.
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False  # Set to True for SQL query debugging in development
)

# Create a sessionmaker instance for executing transactions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Declarative Base for models to inherit from
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Dependency generator function that provides a database session to FastAPI routes.
    Ensures that the session is closed after the request is finished.

    Yields:
        Session: An active SQLAlchemy Session object.
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error("Database session encountered an exception: %s", str(e))
        raise
    finally:
        db.close()


def init_db() -> None:
    """
    Initializes the database by creating all declared tables.
    If the tables already exist, this function does nothing.
    """
    try:
        logger.info("Initializing database tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables initialized successfully.")
    except Exception as e:
        logger.critical("Failed to initialize database tables: %s", str(e))
        raise
