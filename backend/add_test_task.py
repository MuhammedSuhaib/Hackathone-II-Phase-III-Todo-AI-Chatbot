#!/usr/bin/env python
"""
Script to add a test task directly to the database using SQL.
"""
from src.database.connection import get_engine
from sqlmodel import Session
import uuid
from datetime import datetime

if __name__ == "__main__":
    print("Adding test task directly to database...")

    task_id = str(uuid.uuid4())
    title = "Test Task"
    description = "This is a test task"
    completed = False
    user_id = "f37223f9-b590-4e9f-a3d5-f98bcfc0f8ea"  # The user ID we created
    created_at = datetime.utcnow()
    updated_at = datetime.utcnow()

    engine = get_engine()
    with Session(engine) as session:
        try:
            # Insert task directly using SQL
            from sqlalchemy import text
            session.execute(
                text("""
                    INSERT INTO tasks (id, title, description, completed, user_id, created_at, updated_at)
                    VALUES (:id, :title, :description, :completed, :user_id, :created_at, :updated_at)
                """),
                {
                    "id": task_id,
                    "title": title,
                    "description": description,
                    "completed": completed,
                    "user_id": user_id,
                    "created_at": created_at,
                    "updated_at": updated_at
                }
            )
            session.commit()
            print(f"Created task with ID: {task_id}")
        except Exception as e:
            print(f"Error creating task: {e}")
            session.rollback()

    print("Test task setup completed!")