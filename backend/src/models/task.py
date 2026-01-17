from sqlmodel import Field, SQLModel
from datetime import datetime
from typing import Optional
import uuid
from .base import Base
from enum import Enum

class PriorityEnum(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"

class TaskBaseFields:
    """Fields for Task model."""
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    completed: bool = Field(default=False)
    priority: PriorityEnum = Field(default=PriorityEnum.medium)

class Task(TaskBaseFields, Base, table=True):
    """Task model representing a user's todo item."""
    __tablename__ = "tasks"

    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    user_id: str = Field(nullable=False)  # Foreign key to user

class TaskRead(TaskBaseFields, Base):
    """Schema for reading task data."""
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime

class TaskCreate(TaskBaseFields, Base):
    """Schema for creating a new task."""
    user_id: Optional[str] = None  # Will be set by the service to match the authenticated user

class TaskUpdate(SQLModel):
    """Schema for updating an existing task."""
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    completed: Optional[bool] = None
    priority: Optional[PriorityEnum] = None