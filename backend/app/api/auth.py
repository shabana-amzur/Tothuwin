"""
Authentication API Endpoints
Handles user registration, login, and profile management
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.database import get_db
from app.models.database import User
from app.models.user import UserCreate, UserLogin, UserResponse, Token, UserUpdate, PasswordChange
from app.utils.auth import (
    get_password_hash,
    verify_password,
    create_access_token,
    get_current_active_user
)
import logging
import os
import shutil
from pathlib import Path

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(
            (User.email == user_data.email) | (User.username == user_data.username)
        ).first()
        
        if existing_user:
            if existing_user.email == user_data.email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already taken"
                )
        
        # Create new user
        hashed_password = get_password_hash(user_data.password)
        new_user = User(
            email=user_data.email,
            username=user_data.username,
            full_name=user_data.full_name,
            hashed_password=hashed_password,
            is_active=True,
            role="employee"
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        # Create access token
        access_token = create_access_token(
            data={"user_id": new_user.id, "email": new_user.email}
        )
        
        logger.info(f"New user registered: {new_user.email}")
        
        return Token(
            access_token=access_token,
            user=UserResponse.model_validate(new_user)
        )
    
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Database integrity error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email or username already exists"
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Registration error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to register user"
        )


@router.post("/login", response_model=Token)
async def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """Login user and return JWT token"""
    try:
        # Find user by email
        user = db.query(User).filter(User.email == credentials.email).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Verify password
        if not verify_password(credentials.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Check if user is active
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive"
            )
        
        # Create access token
        access_token = create_access_token(
            data={"user_id": user.id, "email": user.email}
        )
        
        logger.info(f"User logged in: {user.email}")
        
        return Token(
            access_token=access_token,
            user=UserResponse.model_validate(user)
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(current_user: User = Depends(get_current_active_user)):
    """Get current user profile"""
    return UserResponse.model_validate(current_user)


@router.put("/update-profile", response_model=UserResponse)
async def update_user_profile(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update user profile information"""
    try:
        # Check if email or username is being changed and if it already exists
        if user_data.email and user_data.email != current_user.email:
            existing_user = db.query(User).filter(User.email == user_data.email).first()
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already in use"
                )
            current_user.email = user_data.email
        
        if user_data.username and user_data.username != current_user.username:
            existing_user = db.query(User).filter(User.username == user_data.username).first()
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already taken"
                )
            current_user.username = user_data.username
        
        if user_data.full_name:
            current_user.full_name = user_data.full_name
        
        db.commit()
        db.refresh(current_user)
        
        logger.info(f"User profile updated: {current_user.email}")
        return UserResponse.model_validate(current_user)
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Profile update error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update profile"
        )


@router.post("/change-password")
async def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Change user password"""
    try:
        # Verify current password
        if not verify_password(password_data.current_password, current_user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )
        
        # Update password
        current_user.hashed_password = get_password_hash(password_data.new_password)
        db.commit()
        
        logger.info(f"Password changed for user: {current_user.email}")
        return {"message": "Password changed successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Password change error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to change password"
        )


@router.post("/upload-profile-picture", response_model=UserResponse)
async def upload_profile_picture(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Upload profile picture"""
    try:
        # Validate file type
        allowed_types = ["image/jpeg", "image/png", "image/jpg", "image/gif", "image/webp"]
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid file type. Only JPEG, PNG, GIF, and WebP images are allowed"
            )
        
        # Create uploads directory if it doesn't exist
        upload_dir = Path("uploads/profile_pictures")
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate unique filename
        file_extension = file.filename.split('.')[-1]
        filename = f"user_{current_user.id}.{file_extension}"
        file_path = upload_dir / filename
        
        # Delete old profile picture if exists
        if current_user.profile_picture:
            old_file_path = Path(current_user.profile_picture)
            if old_file_path.exists() and old_file_path.is_file():
                old_file_path.unlink()
        
        # Save new file
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Update user profile picture path
        current_user.profile_picture = str(file_path)
        db.commit()
        db.refresh(current_user)
        
        logger.info(f"Profile picture uploaded for user: {current_user.email}")
        return UserResponse.model_validate(current_user)
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Profile picture upload error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload profile picture"
        )


@router.delete("/delete-profile-picture", response_model=UserResponse)
async def delete_profile_picture(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete profile picture - only deletes uploaded pictures, reverts to Google picture if exists"""
    try:
        if not current_user.profile_picture:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No profile picture to delete"
            )
        
        # Only delete local uploaded files, not Google profile pictures
        if not current_user.profile_picture.startswith('http'):
            # This is a local uploaded file, delete it
            file_path = Path(current_user.profile_picture)
            if file_path.exists() and file_path.is_file():
                file_path.unlink()
            
            # If user has a Google ID, try to restore their Google profile picture
            if current_user.google_id:
                # Set to None - frontend will show default avatar or we could fetch Google picture again
                current_user.profile_picture = None
                logger.info(f"Deleted uploaded picture for Google user: {current_user.email}, reverting to default")
            else:
                # Regular user, just set to None
                current_user.profile_picture = None
                logger.info(f"Deleted profile picture for user: {current_user.email}")
        else:
            # This is a Google profile picture URL - don't allow deletion, just set to None
            current_user.profile_picture = None
            logger.info(f"Cleared Google profile picture for user: {current_user.email}")
        
        db.commit()
        db.refresh(current_user)
        
        return UserResponse.model_validate(current_user)
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Profile picture deletion error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete profile picture"
        )


@router.get("/health")
async def auth_health():
    """Health check endpoint for auth service"""
    return {"status": "ok", "service": "authentication"}
