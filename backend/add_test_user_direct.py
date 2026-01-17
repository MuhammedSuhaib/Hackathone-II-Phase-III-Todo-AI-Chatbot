#!/usr/bin/env python
"""
Script to add a test user directly to the database using SQL.
"""
from src.database.connection import get_engine
from passlib.context import CryptContext
from sqlmodel import Session
import uuid
from datetime import datetime

# Password hashing context - same as in user_service
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

def hash_password(password: str) -> str:
    """Hash a plain text password."""
    return pwd_context.hash(password)

if __name__ == "__main__":
    print("Adding test user directly to database...")

    # Hash the password
    password_hash = hash_password("pass123")
    user_id = str(uuid.uuid4())
    email = "test@example.com"
    name = "Test User"
    created_at = datetime.utcnow()
    updated_at = datetime.utcnow()

    engine = get_engine()
    with Session(engine) as session:
        try:
            # Check if user already exists
            from sqlalchemy import text
            result = session.execute(text("SELECT * FROM users WHERE email = :email"), {"email": "test@example.com"})
            existing_user = result.fetchone()

            if existing_user:
                print("Test user already exists")
            else:
                # Insert user directly using SQL
                session.execute(
                    text("""
                        INSERT INTO users (id, email, name, hashed_password, created_at, updated_at)
                        VALUES (:id, :email, :name, :hashed_password, :created_at, :updated_at)
                    """),
                    {
                        "id": user_id,
                        "email": email,
                        "name": name,
                        "hashed_password": password_hash,
                        "created_at": created_at,
                        "updated_at": updated_at
                    }
                )
                session.commit()
                print(f"Created user with ID: {user_id}")
        except Exception as e:
            print(f"Error creating user: {e}")
            session.rollback()

    print("Test user setup completed!")