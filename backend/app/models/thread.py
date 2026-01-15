"""
Chat Thread Schemas
Pydantic models for chat thread management
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class ThreadCreate(BaseModel):
    """Schema for creating a new thread"""
    title: Optional[str] = None  # Auto-generated if not provided


class ThreadUpdate(BaseModel):
    """Schema for updating a thread"""
    title: str = Field(..., min_length=1, max_length=255)


class ThreadResponse(BaseModel):
    """Schema for thread response"""
    id: int
    title: str
    created_at: datetime
    updated_at: datetime
    message_count: int = 0
    
    class Config:
        from_attributes = True


class ThreadWithMessages(BaseModel):
    """Schema for thread with its messages"""
    id: int
    title: str
    created_at: datetime
    updated_at: datetime
    messages: List[dict] = []
    
    class Config:
        from_attributes = True
