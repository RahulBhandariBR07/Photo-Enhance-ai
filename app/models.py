"""
Database Models for AI Enchanly.

This module defines the database models representing application schemas,
starting with the 'tasks' schema to track image processing operations.
"""

from datetime import datetime
import uuid
from sqlalchemy import Column, String, DateTime
from sqlalchemy.sql import func
from app.database import Base


class Task(Base):
    """
    Task Model representing an image processing job.

    Attributes:
        task_id (str): Unique UUID string serving as the primary key.
        user_id (str): Identifier of the user who requested the task.
        original_image_path (str): Relative or absolute path to the uploaded image.
        processed_image_path (str): Path to the processed image output (nullable until completed).
        task_type (str): Type of task, e.g., 'enhance' or 'bg-remove'.
        status (str): Task execution status: 'pending', 'processing', 'completed', or 'failed'.
        error_message (str): Log message if the task fails (nullable).
        created_at (datetime): Timestamp representing task creation.
        updated_at (datetime): Timestamp representing the last task update.
    """
    __tablename__ = "tasks"

    task_id = Column(
        String,
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        index=True
    )
    user_id = Column(String, nullable=False, index=True)
    original_image_path = Column(String, nullable=False)
    processed_image_path = Column(String, nullable=True)
    task_type = Column(String, nullable=False)
    status = Column(String, nullable=False, default="pending")
    error_message = Column(String, nullable=True)
    
    # Automatically track timestamps
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        server_default=func.now()
    )
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        server_default=func.now()
    )

    def __repr__(self) -> str:
        return f"<Task(id={self.task_id}, type={self.task_type}, status={self.status})>"
