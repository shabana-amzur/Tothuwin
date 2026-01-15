"""
OAuth API Routes
Handles Google OAuth authentication
"""

from fastapi import APIRouter, HTTPException, status, Depends, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config
import logging
from datetime import timedelta

from ..database import get_db
from ..models.database import User
from ..models.user import Token
from ..utils.auth import create_access_token
from ..config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

router = APIRouter(prefix="/api/auth", tags=["oauth"])

# OAuth Configuration
config = Config(environ={
    "GOOGLE_CLIENT_ID": settings.GOOGLE_CLIENT_ID,
    "GOOGLE_CLIENT_SECRET": settings.GOOGLE_CLIENT_SECRET,
})

oauth = OAuth(config)
oauth.register(
    name='google',
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile'
    }
)


@router.get("/google/login")
async def google_login(request: Request):
    """
    Initiate Google OAuth flow
    Redirects user to Google login page
    """
    redirect_uri = f"{settings.BACKEND_URL}/api/auth/google/callback"
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/google/callback")
async def google_callback(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Handle Google OAuth callback
    Creates or retrieves user and returns JWT token
    """
    try:
        # Get access token from Google
        token = await oauth.google.authorize_access_token(request)
        
        # Get user info from Google
        user_info = token.get('userinfo')
        if not user_info:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to get user info from Google"
            )
        
        email = user_info.get('email')
        name = user_info.get('name', email.split('@')[0])
        google_id = user_info.get('sub')
        
        if not email or not google_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email and Google ID are required"
            )
        
        # Check if user exists by Google ID or email
        user = db.query(User).filter(
            (User.google_id == google_id) | (User.email == email)
        ).first()
        
        if not user:
            # Create new user with unique username
            # If username conflicts, append Google ID suffix
            base_username = name
            username = base_username
            counter = 1
            while db.query(User).filter(User.username == username).first():
                username = f"{base_username}_{counter}"
                counter += 1
            
            user = User(
                email=email,
                username=username,
                full_name=name,  # Set full_name from Google name
                hashed_password="",  # No password for OAuth users
                google_id=google_id,
                is_active=True
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            logger.info(f"Created new Google user: {email} with username: {username}")
        else:
            # Update Google ID if not set
            if not user.google_id:
                user.google_id = google_id
                db.commit()
                db.refresh(user)
                logger.info(f"Updated Google ID for user: {email}")
            else:
                logger.info(f"Existing Google user logged in: {email}")
        
        # Create JWT token
        access_token = create_access_token(
            data={"sub": user.email, "user_id": user.id},
            expires_delta=timedelta(days=settings.ACCESS_TOKEN_EXPIRE_DAYS)
        )
        
        # Redirect to frontend with token in URL
        frontend_url = f"{settings.FRONTEND_URL}/?token={access_token}&email={user.email}&username={user.username}"
        return RedirectResponse(url=frontend_url)
        
    except Exception as e:
        logger.error(f"Google OAuth error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"OAuth authentication failed: {str(e)}"
        )
