from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from ..models.task import Task, TaskCreate, TaskUpdate, TaskRead
from datetime import datetime


class TaskService:
    """
    Service class to handle business logic for Task operations.
    """

    @staticmethod
    def create_task(task_data: TaskCreate, db: Session) -> TaskRead:
        """
        Create a new task.

        Args:
            task_data (TaskCreate): Task data to create
            db (Session): Database session

        Returns:
            TaskRead: Created task data

        Raises:
            HTTPException: If there's an error creating the task
        """
        try:
            # Create a new task instance
            db_task = Task(
                title=task_data.title,
                description=task_data.description,
                completed=task_data.completed,
                priority=task_data.priority,
                user_id=task_data.user_id
            )

            # Add to session and commit
            db.add(db_task)
            db.commit()
            db.refresh(db_task)

            # Return the created task - extract values to avoid serialization issues
            return TaskRead(
                id=db_task.id,
                title=db_task.title,
                description=db_task.description,
                completed=db_task.completed,
                priority=db_task.priority,
                user_id=db_task.user_id,
                created_at=db_task.created_at,
                updated_at=db_task.updated_at
            )
        except IntegrityError as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Error creating task"
            )
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Unexpected error occurred: {str(e)}"
            )

    @staticmethod
    def get_task(task_id: str, user_id: str, db: Session) -> TaskRead:
        """
        Retrieve a specific task by ID for a specific user.

        Args:
            task_id (str): ID of the task to retrieve
            user_id (str): ID of the user who owns the task
            db (Session): Database session

        Returns:
            TaskRead: Retrieved task data

        Raises:
            HTTPException: If task is not found or doesn't belong to user
        """
        try:
            # Query for the task that belongs to the specific user
            db_task = db.query(Task).filter(
                Task.id == task_id,
                Task.user_id == user_id
            ).first()

            if not db_task:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Task not found or does not belong to user"
                )

            # Return the task data - extract values to avoid serialization issues
            return TaskRead(
                id=db_task.id,
                title=db_task.title,
                description=db_task.description,
                completed=db_task.completed,
                priority=db_task.priority,
                user_id=db_task.user_id,
                created_at=db_task.created_at,
                updated_at=db_task.updated_at
            )
        except HTTPException:
            # Re-raise HTTP exceptions
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Unexpected error occurred: {str(e)}"
            )

    @staticmethod
    def get_tasks(user_id: str, db: Session, skip: int = 0, limit: int = 100) -> List[TaskRead]:
        """
        Retrieve all tasks for a specific user.

        Args:
            user_id (str): ID of the user whose tasks to retrieve
            db (Session): Database session
            skip (int): Number of records to skip (for pagination)
            limit (int): Maximum number of records to return (for pagination)

        Returns:
            List[TaskRead]: List of user's tasks
        """
        try:
            # Query for tasks belonging to the specific user with pagination
            db_tasks = db.query(Task).filter(
                Task.user_id == user_id
            ).offset(skip).limit(limit).all()

            # Convert to TaskRead schema - make sure to extract values before session closes
            tasks = []
            for db_task in db_tasks:
                # Extract all values from the ORM object before session might close
                task_dict = {
                    'id': db_task.id,
                    'title': db_task.title,
                    'description': db_task.description,
                    'completed': db_task.completed,
                    'priority': db_task.priority,
                    'user_id': db_task.user_id,
                    'created_at': db_task.created_at,
                    'updated_at': db_task.updated_at
                }

                task = TaskRead(**task_dict)
                tasks.append(task)

            return tasks
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Unexpected error occurred: {str(e)}"
            )

    @staticmethod
    def update_task(task_id: str, user_id: str, task_update: TaskUpdate, db: Session) -> TaskRead:
        """
        Update an existing task.

        Args:
            task_id (str): ID of the task to update
            user_id (str): ID of the user who owns the task
            task_update (TaskUpdate): Updated task data
            db (Session): Database session

        Returns:
            TaskRead: Updated task data

        Raises:
            HTTPException: If task is not found or doesn't belong to user
        """
        try:
            # Query for the task that belongs to the specific user
            db_task = db.query(Task).filter(
                Task.id == task_id,
                Task.user_id == user_id
            ).first()

            if not db_task:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Task not found or does not belong to user"
                )

            # Update fields if they are provided in the update data
            update_data = task_update.model_dump(exclude_unset=True) if hasattr(task_update, 'model_dump') else task_update.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_task, field, value)

            # Commit the changes
            db.commit()
            db.refresh(db_task)

            # Return the updated task - extract values to avoid serialization issues
            return TaskRead(
                id=db_task.id,
                title=db_task.title,
                description=db_task.description,
                completed=db_task.completed,
                priority=db_task.priority,
                user_id=db_task.user_id,
                created_at=db_task.created_at,
                updated_at=db_task.updated_at
            )
        except IntegrityError as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Error updating task"
            )
        except HTTPException:
            # Re-raise HTTP exceptions
            raise
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Unexpected error occurred: {str(e)}"
            )

    @staticmethod
    def delete_task(task_id: str, user_id: str, db: Session) -> bool:
        """
        Delete a specific task by ID for a specific user.

        Args:
            task_id (str): ID of the task to delete
            user_id (str): ID of the user who owns the task
            db (Session): Database session

        Returns:
            bool: True if task was deleted, False otherwise

        Raises:
            HTTPException: If task is not found or doesn't belong to user
        """
        try:
            # Query for the task that belongs to the specific user
            db_task = db.query(Task).filter(
                Task.id == task_id,
                Task.user_id == user_id
            ).first()

            if not db_task:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Task not found or does not belong to user"
                )

            # Delete the task
            db.delete(db_task)
            db.commit()

            return True
        except HTTPException:
            # Re-raise HTTP exceptions
            raise
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Unexpected error occurred: {str(e)}"
            )

    @staticmethod
    def toggle_task_completion(task_id: str, user_id: str, db: Session) -> TaskRead:
        """
        Toggle the completion status of a task.

        Args:
            task_id (str): ID of the task to toggle
            user_id (str): ID of the user who owns the task
            db (Session): Database session

        Returns:
            TaskRead: Updated task data with toggled completion status

        Raises:
            HTTPException: If task is not found or doesn't belong to user
        """
        try:
            # Query for the task that belongs to the specific user
            db_task = db.query(Task).filter(
                Task.id == task_id,
                Task.user_id == user_id
            ).first()

            if not db_task:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Task not found or does not belong to user"
                )

            # Toggle the completion status
            db_task.completed = not db_task.completed

            # Update the updated_at timestamp (handled by the Base model's __setattr__)
            from datetime import datetime
            db_task.updated_at = datetime.utcnow()

            # Commit the changes
            db.commit()
            db.refresh(db_task)

            # Return the updated task - extract values to avoid serialization issues
            return TaskRead(
                id=db_task.id,
                title=db_task.title,
                description=db_task.description,
                completed=db_task.completed,
                priority=db_task.priority,
                user_id=db_task.user_id,
                created_at=db_task.created_at,
                updated_at=db_task.updated_at
            )
        except HTTPException:
            # Re-raise HTTP exceptions
            raise
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Unexpected error occurred: {str(e)}"
            )