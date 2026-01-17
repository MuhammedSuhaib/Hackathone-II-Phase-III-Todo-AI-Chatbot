#!/usr/bin/env python
"""
Script to add a test user to the database.
"""
from src.database.connection import get_engine
from src.services.user_service import UserService
from src.models.user import UserCreate
from sqlmodel import Session

if __name__ == "__main__":
    print("Adding test user to database...")

    # Create a user
    user_data = UserCreate(
        email="test@example.com",
        name="Test User",
        password="pass123",
        confirm_password="pass123"
    )

    engine = get_engine()
    with Session(engine) as session:
        try:
            # Check if user already exists
            from sqlalchemy import text
            result = session.execute(text("SELECT * FROM public.user WHERE email = :email"), {"email": "test@example.com"})
            existing_user = result.fetchone()

            if existing_user:
                print("Test user already exists")
            else:
                # Create new user
                created_user = UserService.create_user(user_data, session)
                print(f"Created user with ID: {created_user.id}")
        except Exception as e:
            print(f"Error creating user: {e}")
            session.rollback()

    print("Test user setup completed!")