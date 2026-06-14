"""
Pydantic Schemas for AI Enchanly.

This module defines models for request validation and API serialization schemas.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class TaskBase(BaseModel):
    """Base Pydantic model for Task data common to requests and responses."""
    user_id: str = Field(..., description="Unique identifier of the user requesting the task")
    task_type: str = Field(..., description="Type of image processing task: 'enhance' or 'bg-remove'")


class TaskCreateResponse(BaseModel):
    """Schema returned immediately after queuing a task."""
    task_id: str
    status: str
    message: str


class TaskResponse(BaseModel):
    """Complete serialization model for returning Task details to client apps."""
    task_id: str
    user_id: str
    original_image_path: str
    processed_image_path: Optional[str] = None
    task_type: str
    status: str
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    # Enable integration with SQLAlchemy objects (Pydantic v2 config)
    model_config = ConfigDict(from_attributes=True)


class TaskUpdate(BaseModel):
    """Schema used internally to update task status and outcomes in the DB."""
    status: str
    processed_image_path: Optional[str] = None
    error_message: Optional[str] = None
