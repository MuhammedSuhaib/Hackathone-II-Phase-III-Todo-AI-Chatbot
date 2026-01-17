from sqlalchemy import Column, String, create_engine
from sqlalchemy.orm import sessionmaker
from src.models.task import Task
from src.config.settings import settings
from sqlmodel import Session

# Create database engine
engine = create_engine(settings.DATABASE_URL)

# Create a session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

# Add priority column to existing tasks if it doesn't exist
try:
    # Add priority column using raw SQL
    with engine.connect() as conn:
        # Check if priority column exists
        result = conn.execute(
            "SELECT column_name FROM information_schema.columns WHERE table_name = 'tasks' AND column_name = 'priority'"
        )
        if not result.fetchone():
            # Add priority column with default value
            conn.execute("ALTER TABLE tasks ADD COLUMN priority VARCHAR(20) DEFAULT 'medium'")
            conn.commit()
            print("Priority column added successfully")
        else:
            print("Priority column already exists")
except Exception as e:
    print(f"Error adding priority column: {e}")
finally:
    db.close()