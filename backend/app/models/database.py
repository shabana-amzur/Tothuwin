"""
Database Models
Defines User and ChatHistory tables
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class User(Base):
    """User model for employee authentication"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    google_id = Column(String(255), unique=True, nullable=True, index=True)  # For Google OAuth
    is_active = Column(Boolean, default=True, nullable=False)
    role = Column(String(50), default="employee", nullable=False)  # employee, admin
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationship
    chat_threads = relationship("ChatThread", back_populates="user", cascade="all, delete-orphan")
    chat_histories = relationship("ChatHistory", back_populates="user", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="user", cascade="all, delete-orphan")


class ChatThread(Base):
    """Chat thread model to organize conversations"""
    __tablename__ = "chat_threads"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationship
    user = relationship("User", back_populates="chat_threads")
    messages = relationship("ChatHistory", back_populates="thread", cascade="all, delete-orphan", order_by="ChatHistory.created_at")


class ChatHistory(Base):
    """Chat history model to store conversations"""
    __tablename__ = "chat_histories"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    thread_id = Column(Integer, ForeignKey("chat_threads.id"), nullable=True, index=True)
    message = Column(Text, nullable=False)  # User message
    response = Column(Text, nullable=False)  # AI response
    model = Column(String(100), nullable=False)  # Model used (e.g., gemini-2.5-flash)
    session_id = Column(String(100), index=True)  # Optional: group messages by session
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship
    user = relationship("User", back_populates="chat_histories")
    thread = relationship("ChatThread", back_populates="messages")

class Document(Base):
    """Document model for uploaded files"""
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    thread_id = Column(Integer, ForeignKey("chat_threads.id"), nullable=True, index=True)  # Thread-specific documents
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False)  # Size in bytes
    file_type = Column(String(50), nullable=False)  # pdf, txt, docx
    status = Column(String(50), default="processing", nullable=False)  # processing, ready, failed
    chunk_count = Column(Integer, default=0)  # Number of chunks created
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship
    user = relationship("User", back_populates="documents")
    thread = relationship("ChatThread", foreign_keys=[thread_id])