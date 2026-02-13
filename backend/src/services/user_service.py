from sqlalchemy.orm import Session
from ..models.user import User, UserCreate
from passlib.context import CryptContext
from typing import Optional
from fastapi import HTTPException, status
import uuid
from ..utils.logging_config import get_logger

# Password hashing context - using pbkdf2_sha256 as bcrypt is having issues
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


class UserService:
    logger = get_logger(__name__)

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a plain text password."""
        UserService.logger.debug(f"Hashing password for user")
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a plain text password against a hashed password."""
        UserService.logger.debug(f"Verifying password")
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def create_user(user_data: UserCreate, db: Session) -> User:
        """
        Create a new user in the database.

        Args:
            user_data (UserCreate): User creation data
            db (Session): Database session

        Returns:
            User: Created user object
        """
        UserService.logger.info(f"Creating user with email: {user_data.email}")

        # Hash the password
        from datetime import datetime
        hashed_password = UserService.hash_password(user_data.password)

        # Generate a new user ID
        import uuid
        user_id = str(uuid.uuid4())
        UserService.logger.debug(f"Generated user ID: {user_id}")

        # Insert user using raw SQL to avoid session compatibility issues
        from sqlalchemy import text
        db.execute(
            text("""
                INSERT INTO users (id, email, name, hashed_password, created_at, updated_at)
                VALUES (:id, :email, :name, :hashed_password, :created_at, :updated_at)
            """),
            {
                "id": user_id,
                "email": user_data.email,
                "name": user_data.name,
                "hashed_password": hashed_password,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
        )
        db.commit()
        UserService.logger.info(f"User created successfully with ID: {user_id}")

        # Return the created user
        return User(
            id=user_id,
            email=user_data.email,
            name=user_data.name,
            hashed_password=hashed_password,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

    @staticmethod
    def get_user_by_id(user_id: str, db: Session) -> Optional[User]:
        """
        Get a user by ID.

        Args:
            user_id (str): User ID
            db (Session): Database session

        Returns:
            User: User object if found, None otherwise
        """
        UserService.logger.debug(f"Retrieving user by ID: {user_id}")

        from sqlalchemy import text
        result = db.execute(
            text("SELECT id, email, name, hashed_password, created_at, updated_at FROM users WHERE id = :user_id LIMIT 1"),
            {"user_id": user_id}
        ).fetchone()

        if result:
            UserService.logger.debug(f"User found with ID: {user_id}")
            return User(
                id=result.id,
                email=result.email,
                name=result.name,
                hashed_password=result.hashed_password,
                created_at=result.created_at,
                updated_at=result.updated_at
            )
        UserService.logger.debug(f"User not found with ID: {user_id}")
        return None

    @staticmethod
    def get_user_by_email(email: str, db: Session) -> Optional[User]:
        """
        Get a user by email.

        Args:
            email (str): User email
            db (Session): Database session

        Returns:
            User: User object if found, None otherwise
        """
        UserService.logger.debug(f"Retrieving user by email: {email}")

        from sqlalchemy import text
        result = db.execute(
            text("SELECT id, email, name, hashed_password, created_at, updated_at FROM users WHERE email = :email LIMIT 1"),
            {"email": email}
        ).fetchone()

        if result:
            UserService.logger.debug(f"User found with email: {email}")
            from datetime import datetime
            return User(
                id=result.id,
                email=result.email,
                name=result.name,
                hashed_password=result.hashed_password,
                created_at=result.created_at,
                updated_at=result.updated_at
            )
        UserService.logger.debug(f"User not found with email: {email}")
        return None

    @staticmethod
    def authenticate_user(email: str, password: str, db: Session) -> Optional[User]:
        """
        Authenticate a user by email and password.

        Args:
            email (str): User email
            password (str): Plain text password
            db (Session): Database session

        Returns:
            User: Authenticated user object if credentials are valid, None otherwise
        """
        UserService.logger.info(f"Authenticating user with email: {email}")

        # Get user by email using raw SQL to avoid session compatibility issues
        from sqlalchemy import text
        result = db.execute(
            text("SELECT id, email, name, hashed_password, created_at, updated_at FROM users WHERE email = :email LIMIT 1"),
            {"email": email}
        ).fetchone()

        if not result:
            UserService.logger.warning(f"Authentication failed: User with email {email} not found")
            return None

        # Convert to User object
        from datetime import datetime
        user = User(
            id=result.id,
            email=result.email,
            name=result.name,
            hashed_password=result.hashed_password,
            created_at=result.created_at,
            updated_at=result.updated_at
        )

        # Check if password is correct
        if not UserService.verify_password(password, user.hashed_password):
            UserService.logger.warning(f"Authentication failed: Incorrect password for email {email}")
            return None

        UserService.logger.info(f"User authenticated successfully: {user.id}")
        return user

    @staticmethod
    def update_user(user_id: str, user_update_data: dict, db: Session) -> Optional[User]:
        """
        Update a user's information.

        Args:
            user_id (str): User ID
            user_update_data (dict): Data to update
            db (Session): Database session

        Returns:
            User: Updated user object if successful, None otherwise
        """
        UserService.logger.info(f"Updating user with ID: {user_id}, data: {user_update_data}")

        # Get user by ID to check if it exists
        user = UserService.get_user_by_id(user_id, db)

        if not user:
            UserService.logger.warning(f"Update failed: User with ID {user_id} not found")
            return None

        # Build update query dynamically
        from sqlalchemy import text
        from datetime import datetime
        import uuid

        # Prepare update fields
        update_fields = []
        params = {"user_id": user_id, "updated_at": datetime.utcnow()}

        for field, value in user_update_data.items():
            if value is not None and field in ['name', 'email']:  # Only allow updating specific fields
                update_fields.append(f"{field} = :{field}")
                params[field] = value

        if not update_fields:
            # If no fields to update, just update the timestamp
            UserService.logger.debug(f"No fields to update for user {user_id}, updating timestamp only")
            query = text("UPDATE users SET updated_at = :updated_at WHERE id = :user_id")
        else:
            # Add the updated_at field to the update
            update_fields.append("updated_at = :updated_at")
            query = text(f"UPDATE users SET {', '.join(update_fields)} WHERE id = :user_id")

        # Execute the update
        db.execute(query, params)
        db.commit()
        UserService.logger.info(f"User updated successfully: {user_id}")

        # Return updated user
        return UserService.get_user_by_id(user_id, db)

    @staticmethod
    def delete_user(user_id: str, db: Session) -> bool:
        """
        Delete a user.

        Args:
            user_id (str): User ID
            db (Session): Database session

        Returns:
            bool: True if deletion was successful, False otherwise
        """
        UserService.logger.info(f"Deleting user with ID: {user_id}")

        # Check if user exists
        user = UserService.get_user_by_id(user_id, db)

        if not user:
            UserService.logger.warning(f"Deletion failed: User with ID {user_id} not found")
            return False

        # Delete user using raw SQL to avoid session compatibility issues
        from sqlalchemy import text
        db.execute(
            text("DELETE FROM users WHERE id = :user_id"),
            {"user_id": user_id}
        )
        db.commit()
        UserService.logger.info(f"User deleted successfully: {user_id}")

        return True