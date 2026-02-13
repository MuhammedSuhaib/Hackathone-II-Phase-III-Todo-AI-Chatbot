"""
MCP Tool: add_task
This tool allows the AI agent to create a new task for a user.
"""

from typing import Dict, Any
from ..server import mcp_server
from sqlmodel import Session, select
from ...models.task import Task, TaskCreate, PriorityEnum
from contextlib import contextmanager
from ...utils.logging_config import get_logger


logger = get_logger(__name__)


def get_valid_priority(priority: str) -> PriorityEnum:
    """Convert string priority to PriorityEnum."""
    if isinstance(priority, PriorityEnum):
        return priority

    priority_lower = priority.lower()
    if priority_lower in ["low", "medium", "high"]:
        return PriorityEnum(priority_lower)
    return PriorityEnum.medium  # Default to medium if invalid


@mcp_server.register_tool("add_task")
async def add_task(user_id: str, title: str, description: str = "", priority: str = "medium") -> Dict[str, Any]:
    """
    Create a new task for the specified user.

    Args:
        user_id: The ID of the user for whom to create the task
        title: The title of the task
        description: Optional description of the task
        priority: Priority level ('low', 'medium', 'high') - defaults to 'medium'

    Returns:
        Dictionary containing the created task information
    """
    logger.info(f"Executing add_task tool for user: {user_id}, title: {title}")

    try:
        # Import database session here to avoid circular imports
        from sqlmodel import Session
        from src.database.connection import engine
        from src.services.task_service import TaskService
        from src.models.task import TaskCreate

        # Validate inputs
        if not title.strip():
            logger.warning("Task title cannot be empty")
            return {
                "success": False,
                "error": "Task title cannot be empty"
            }

        # Validate and convert priority
        validated_priority = get_valid_priority(priority)
        logger.debug(f"Validated priority: {validated_priority}")

        # Create database session
        with Session(engine) as db_session:
            logger.debug("Creating database session for add_task")

            # Create task using the TaskService
            task_create = TaskCreate(
                user_id=user_id,
                title=title,
                description=description,
                priority=validated_priority,
                completed=False
            )

            task_service = TaskService()
            created_task = task_service.create_task(task_create, db_session)

            # Convert to dict for response
            task_dict = {
                "id": created_task.id,
                "user_id": created_task.user_id,
                "title": created_task.title,
                "description": created_task.description,
                "completed": created_task.completed,
                "priority": created_task.priority.value if hasattr(created_task.priority, 'value') else created_task.priority,
                "created_at": created_task.created_at.isoformat() if hasattr(created_task.created_at, 'isoformat') else str(created_task.created_at),
                "updated_at": created_task.updated_at.isoformat() if hasattr(created_task.updated_at, 'isoformat') else str(created_task.updated_at)
            }

            logger.info(f"Task created successfully with ID: {created_task.id}")
            return {
                "success": True,
                "task": task_dict
            }
    except Exception as e:
        logger.error(f"Failed to add task: {str(e)}")
        return {
            "success": False,
            "error": f"Failed to add task: {str(e)}"
        }


# For integration with the existing Phase II task system
def add_task_with_db_session(user_id: str, title: str, description: str = "", priority: str = "medium", db_session: Session = None) -> Dict[str, Any]:
    """
    Create a new task for the specified user using database session.

    Args:
        user_id: The ID of the user for whom to create the task
        title: The title of the task
        description: Optional description of the task
        priority: Priority level ('low', 'medium', 'high') - defaults to 'medium'
        db_session: Database session to use for the operation

    Returns:
        Dictionary containing the created task information
    """
    logger.info(f"Executing add_task_with_db_session for user: {user_id}, title: {title}")

    try:
        # Validate inputs
        if not title.strip():
            logger.warning("Task title cannot be empty")
            return {
                "success": False,
                "error": "Task title cannot be empty"
            }

        # Validate and convert priority
        validated_priority = get_valid_priority(priority)
        logger.debug(f"Validated priority: {validated_priority}")

        # Create the task object using the Task model from Phase II
        task_create = TaskCreate(
            user_id=user_id,
            title=title,
            description=description,
            priority=validated_priority
        )

        # Create task instance
        task = Task.from_orm(task_create)

        # Add to database
        db_session.add(task)
        db_session.commit()
        db_session.refresh(task)

        # Convert to dictionary for response
        task_dict = {
            "id": task.id,
            "user_id": task.user_id,
            "title": task.title,
            "description": task.description,
            "completed": task.completed,
            "priority": task.priority.value if hasattr(task.priority, 'value') else task.priority,
            "created_at": getattr(task, 'created_at', None),
            "updated_at": getattr(task, 'updated_at', None)
        }

        logger.info(f"Task created successfully with ID: {task.id}")
        return {
            "success": True,
            "task": task_dict
        }
    except Exception as e:
        logger.error(f"Failed to add task: {str(e)}")
        return {
            "success": False,
            "error": f"Failed to add task: {str(e)}"
        }