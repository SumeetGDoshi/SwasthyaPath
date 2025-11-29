"""
Authentication routes for signup, login, token refresh, and logout.
"""

from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import ValidationError

from models.schemas import (
    UserSignup,
    UserLogin,
    TokenResponse,
    RefreshTokenRequest,
    UserResponse,
)
from utils.auth_utils import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    verify_token,
    REFRESH_TOKEN_EXPIRE_DAYS,
)
from database.supabase_client import get_db
from middleware.auth_middleware import get_current_user

# Create router
router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def signup(user_data: UserSignup):
    """
    Register a new user account.
    
    Creates a new user with email/password authentication and returns
    access and refresh tokens for immediate login.
    """
    try:
        db = get_db()
        
        # Check if user already exists
        existing_user = db.get_user_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Hash password
        password_hash = hash_password(user_data.password)
        
        # Create user
        user = db.create_auth_user(
            email=user_data.email,
            password_hash=password_hash,
            name=user_data.name,
            phone=user_data.phone
        )
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user"
            )
        
        # Create access and refresh tokens
        token_data = {"sub": user["id"], "email": user["email"]}
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)
        
        # Store refresh token
        expires_at = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        db.store_refresh_token(user["id"], refresh_token, expires_at)
        
        # Return tokens and user info
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            user={
                "id": user["id"],
                "email": user["email"],
                "name": user["name"],
                "phone": user.get("phone")
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during signup: {str(e)}"
        )


@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin):
    """
    Log in with email and password.
    
    Validates credentials and returns access and refresh tokens.
    """
    try:
        db = get_db()
        
        # Get user by email
        user = db.get_user_by_email(credentials.email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Verify password
        if not verify_password(credentials.password, user.get("password_hash", "")):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Check if user is active
        if not user.get("is_active", True):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is disabled"
            )
        
        # Create tokens
        token_data = {"sub": user["id"], "email": user["email"]}
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)
        
        # Store refresh token
        expires_at = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        db.store_refresh_token(user["id"], refresh_token, expires_at)
        
        # Return tokens and user info
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            user={
                "id": user["id"],
                "email": user["email"],
                "name": user["name"],
                "phone": user.get("phone")
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during login: {str(e)}"
        )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_access_token(request: RefreshTokenRequest):
    """
    Refresh access token using a valid refresh token.
    
    Returns a new access token while keeping the same refresh token.
    """
    try:
        db = get_db()
        
        # Verify refresh token
        payload = verify_token(request.refresh_token, token_type="refresh")
        if payload is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token"
            )
        
        # Check if refresh token exists in database
        token_record = db.get_refresh_token(request.refresh_token)
        if not token_record:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token not found or revoked"
            )
        
        # Check if token is expired
        expires_at = datetime.fromisoformat(token_record["expires_at"].replace("Z", "+00:00"))
        if datetime.utcnow() > expires_at.replace(tzinfo=None):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token has expired"
            )
        
        # Get user
        user_id = payload.get("sub")
        user = db.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Create new access token
        token_data = {"sub": user["id"], "email": user.get("email")}
        access_token = create_access_token(token_data)
        
        # Return new access token with same refresh token
        return TokenResponse(
            access_token=access_token,
            refresh_token=request.refresh_token,
            user={
                "id": user["id"],
                "email": user.get("email"),
                "name": user["name"],
                "phone": user.get("phone")
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during token refresh: {str(e)}"
        )


@router.post("/logout")
async def logout(request: RefreshTokenRequest):
    """
    Log out by revoking the refresh token.
    
    This prevents the refresh token from being used to obtain new access tokens.
    """
    try:
        db = get_db()
        
        # Revoke the refresh token
        success = db.revoke_refresh_token(request.refresh_token)
        
        return {
            "success": success,
            "message": "Logged out successfully" if success else "Token not found"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during logout: {str(e)}"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """
    Get current authenticated user information.
    
    Requires valid access token in Authorization header.
    """
    return UserResponse(
        id=current_user["id"],
        email=current_user.get("email", ""),
        name=current_user["name"],
        phone=current_user.get("phone"),
        age=current_user.get("age"),
        gender=current_user.get("gender"),
        created_at=current_user.get("created_at", datetime.now().isoformat())
    )
