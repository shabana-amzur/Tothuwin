"""
Document Schemas
Pydantic models for document upload and management
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class DocumentUploadResponse(BaseModel):
    """Response after document upload"""
    id: int
    filename: str
    original_filename: str
    file_size: int
    file_type: str
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class DocumentListItem(BaseModel):
    """Document list item"""
    id: int
    filename: str
    original_filename: str
    file_size: int
    file_type: str
    status: str
    chunk_count: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class DocumentDelete(BaseModel):
    """Response after document deletion"""
    message: str
    document_id: int
