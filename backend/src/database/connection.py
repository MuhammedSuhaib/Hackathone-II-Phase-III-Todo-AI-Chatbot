from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool
from ..config.settings import settings
from sqlmodel import create_engine as sqlmodel_create_engine
from ..utils.logging_config import get_logger

# Import models to ensure they are registered with SQLModel's metadata
from ..models import task  # noqa: F401
from ..models import user  # noqa: F401
from ..models import conversation, message  # noqa: F401


# Configure logging
logger = get_logger(__name__)


def create_db_engine():
    """
    Create and configure the database engine with appropriate settings for Neon Serverless PostgreSQL.

    Returns:
        Engine: SQLAlchemy engine instance configured for the database
    """
    logger.info(f"Creating database engine for: {'SQLite' if settings.NEON_DB_URL.startswith('sqlite') else 'PostgreSQL'}")

    # Check if we're using SQLite (for local development) or PostgreSQL
    if settings.NEON_DB_URL.startswith("sqlite"):
        logger.debug("Configuring SQLite engine (no connection pooling)")
        # SQLite doesn't support connect_timeout or connection pooling
        engine = sqlmodel_create_engine(
            settings.NEON_DB_URL,
            echo=False,  # Set to True for SQL query logging (useful for debugging)
        )
    else:
        logger.debug("Configuring PostgreSQL engine with connection pooling")
        # Use SQLModel's create_engine which is compatible with both SQLAlchemy and SQLModel
        # with connection pooling for PostgreSQL
        engine = sqlmodel_create_engine(
            settings.NEON_DB_URL,
            # Connection pool settings optimized for serverless environments
            poolclass=QueuePool,
            pool_size=5,  # Number of connections to maintain in the pool
            max_overflow=10,  # Additional connections beyond pool_size
            pool_pre_ping=True,  # Verify connections before use
            pool_recycle=300,  # Recycle connections after 5 minutes
            echo=False,  # Set to True for SQL query logging (useful for debugging)
            connect_args={
                # Additional connection arguments specific to PostgreSQL
                "connect_timeout": 10,  # Timeout for establishing connection
            }
        )

    logger.info("Database engine created successfully")
    return engine


# Create the global engine instance
engine = create_db_engine()


def get_engine():
    """
    Get the database engine instance.

    Returns:
        Engine: The configured database engine
    """
    logger.debug("Retrieving database engine instance")
    return engine


def create_tables():
    """
    Create all database tables based on the registered models.
    """
    logger.info("Creating database tables...")
    from sqlmodel import SQLModel
    SQLModel.metadata.create_all(engine)
    logger.info("Database tables created successfully")


def ping_database():
    """
    Test the database connection by attempting to connect.

    Returns:
        bool: True if connection is successful, False otherwise
    """
    logger.debug("Testing database connection...")
    from sqlalchemy import text
    try:
        with engine.connect() as conn:
            # Execute a simple query to test the connection
            result = conn.execute(text("SELECT 1"))
            logger.debug("Database ping successful")
            return result.fetchone()[0] == 1
    except Exception as e:
        logger.error(f"Database ping failed: {str(e)}")
        return False


# Test the connection when the module is loaded
if __name__ != "__main__":
    logger.info("Testing database connection on startup...")
    if not ping_database():
        logger.warning("Warning: Could not establish database connection")
    else:
        logger.info("Database connection established successfully")