#!/usr/bin/env python
"""
Script to drop and recreate database tables in PostgreSQL.
"""
from src.database.connection import get_engine
from sqlmodel import SQLModel, Session

def recreate_tables():
    print("Dropping and recreating database tables...")

    engine = get_engine()

    # Drop all tables first
    from sqlalchemy import inspect, text

    # Get table names
    inspector = inspect(engine)
    table_names = inspector.get_table_names()

    print(f"Existing tables: {table_names}")

    # Drop tables manually since SQLModel doesn't have a clean way to drop all
    with engine.connect() as conn:
        for table_name in table_names:
            print(f"Dropping table: {table_name}")
            try:
                # Use raw SQL to drop the table
                conn.execute(text(f'DROP TABLE IF EXISTS "{table_name}" CASCADE'))
            except Exception as e:
                print(f"Error dropping table {table_name}: {e}")

        conn.commit()

    # Now create the tables again
    SQLModel.metadata.create_all(engine)
    print("Tables recreated successfully!")

if __name__ == "__main__":
    recreate_tables()