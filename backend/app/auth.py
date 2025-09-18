"""
Authentication and JWT utilities for Son1kVers3
"""
import os
import jwt
import bcrypt
from datetime import datetime, timedelta
from typing import Optional
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import uuid

from .db import get_db_session
from .models import User, UserPlan, PLAN_LIMITS
from .settings import settings

# JWT Configuration
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24

security = HTTPBearer()

def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_access_token(user_id: str, email: str) -> str:
    """Create JWT access token"""
    expire = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    payload = {
        "sub": user_id,
        "email": email,
        "exp": expire,
        "iat": datetime.utcnow()
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str) -> Optional[dict]:
    """Verify and decode JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        email = payload.get("email")
        
        if user_id is None or email is None:
            return None
            
        return {"user_id": user_id, "email": email}
    except jwt.PyJWTError:
        return None

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current authenticated user"""
    token = credentials.credentials
    payload = verify_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    with get_db_session() as db:
        user = db.query(User).filter(User.id == payload["user_id"]).first()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        # Reset daily usage if needed
        if user.last_usage_reset.date() < datetime.utcnow().date():
            user.daily_usage = 0
            user.last_usage_reset = datetime.utcnow()
            db.commit()
            
        return user

def create_user(email: str, password: str, name: Optional[str] = None) -> User:
    """Create new user"""
    with get_db_session() as db:
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create new user
        user_id = str(uuid.uuid4())
        hashed_password = hash_password(password)
        
        user = User(
            id=user_id,
            email=email,
            hashed_password=hashed_password,
            plan=UserPlan.FREE,
            daily_usage=0,
            monthly_usage=0,
            last_usage_reset=datetime.utcnow(),
            created_at=datetime.utcnow(),
            is_active=True
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        return user

def authenticate_user(email: str, password: str) -> Optional[User]:
    """Authenticate user by email and password"""
    with get_db_session() as db:
        user = db.query(User).filter(User.email == email).first()
        if not user or not verify_password(password, user.hashed_password):
            return None
        return user

def get_user_limits(user: User) -> dict:
    """Get user's current limits and usage"""
    plan_config = PLAN_LIMITS.get(user.plan, PLAN_LIMITS[UserPlan.FREE])
    
    return {
        "daily_usage": user.daily_usage,
        "daily_limit": plan_config["daily_limit"],
        "monthly_usage": user.monthly_usage,
        "monthly_limit": plan_config["monthly_limit"],
        "can_create_job": (
            (plan_config["daily_limit"] == -1 or user.daily_usage < plan_config["daily_limit"]) and
            (plan_config["monthly_limit"] == -1 or user.monthly_usage < plan_config["monthly_limit"])
        )
    }