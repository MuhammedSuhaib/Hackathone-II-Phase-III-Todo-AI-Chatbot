from contextlib import contextmanager
from sqlalchemy.orm import Session, sessionmaker
from typing import Generator
from .connection import engine
from ..utils.logging_config import get_logger


# Configure logging
logger = get_logger(__name__)

# Create a session factory bound to the engine
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
logger.debug("Database session factory created")


def get_session() -> Generator[Session, None, None]:
    """
    Dependency to get database session for FastAPI endpoints.

    Yields:
        Session: SQLAlchemy database session
    """
    logger.debug("Creating new database session for FastAPI endpoint")
    db = SessionLocal()
    try:
        yield db
    finally:
        logger.debug("Closing database session for FastAPI endpoint")
        db.close()


@contextmanager
def get_db_session():
    """
    Context manager to get database session for use outside of FastAPI endpoints.

    Yields:
        Session: SQLAlchemy database session
    """
    logger.debug("Creating new database session via context manager")
    db = SessionLocal()
    try:
        yield db
    finally:
        logger.debug("Closing database session via context manager")
        db.close()


def get_session_sync() -> Session:
    """
    Synchronous function to get database session.

    Returns:
        Session: SQLAlchemy database session (remember to close it manually)
    """
    logger.debug("Creating synchronous database session")
    return SessionLocal()


def close_session(db: Session):
    """
    Close the database session.

    Args:
        db (Session): SQLAlchemy database session to close
    """
    logger.debug("Manually closing database session")
    db.close()


# Convenience function to run database operations with automatic session management
def run_db_operation(operation_func, *args, **kwargs):
    """
    Run a database operation with automatic session management.

    Args:
        operation_func: Function to run with database session
        *args: Arguments to pass to the operation function
        **kwargs: Keyword arguments to pass to the operation function

    Returns:
        Result of the operation function
    """
    logger.debug(f"Running database operation: {operation_func.__name__}")
    with get_db_session() as db:
        kwargs['db'] = db
        result = operation_func(*args, **kwargs)
        logger.debug(f"Database operation completed: {operation_func.__name__}")
        return result