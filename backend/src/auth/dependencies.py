from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Generator
from .jwt_handler import verify_token, get_current_user
from ..database.session import get_session
from ..models.task import Task


security = HTTPBearer()


def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """
    Dependency to get current user ID from JWT token.

    Args:
        credentials (HTTPAuthorizationCredentials): Bearer token from Authorization header

    Returns:
        str: User ID extracted from token

    Raises:
        HTTPException: If token is invalid or missing
    """
    token = credentials.credentials
    payload = verify_token(token)
    user_id = payload.get("sub")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )

    return user_id


def verify_user_owns_task(
    user_id: str = Depends(get_current_user_id),
    task_id: str = None,
    db: Session = Depends(get_session)
) -> bool:
    """
    Verify that the current user owns the specified task.

    Args:
        user_id (str): User ID from JWT token (automatically extracted)
        task_id (str): Task ID to verify ownership for
        db (Session): Database session

    Returns:
        bool: True if user owns the task, raises HTTPException otherwise

    Raises:
        HTTPException: If user doesn't own the task
    """
    if not task_id:
        return True

    # Query the task by ID
    task = db.get(Task, task_id)

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    if task.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this task"
        )

    return True


def get_user_tasks_query(user_id: str = Depends(get_current_user_id)):
    """
    Get a query object filtered by the current user's tasks.

    Args:
        user_id (str): User ID from JWT token (automatically extracted)

    Returns:
        Callable: Function that returns a filtered query
    """
    def _get_filtered_query(db: Session = Depends(get_session)):
        return db.query(Task).filter(Task.user_id == user_id)

    return _get_filtered_query


def validate_user_id_in_path(request: Request, current_user_id: str = Depends(get_current_user_id)):
    """
    Validate that the user_id in the URL path matches the user_id in the JWT token.

    Args:
        request (Request): FastAPI request object to extract path parameters
        current_user_id (str): User ID from JWT token (automatically extracted)

    Returns:
        str: User ID if validation passes

    Raises:
        HTTPException: If user IDs don't match
    """
    # Extract user_id from path
    path_user_id = request.path_params.get('user_id')

    if not path_user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User ID not found in path"
        )

    if path_user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this user's data"
        )

    return current_user_id