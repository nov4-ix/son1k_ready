from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey, Float, Enum, Boolean, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import enum
from .db import Base

# Job status enum for better type safety
class JobStatus(str, enum.Enum):
    QUEUED = "queued"
    ASSIGNED = "assigned"  
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"

# User plan enum
class UserPlan(str, enum.Enum):
    FREE = "free"
    PRO = "pro" 
    ENTERPRISE = "enterprise"

class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String, nullable=True)  # For authentication
    plan = Column(String, default=UserPlan.FREE)
    
    # Usage tracking
    daily_usage = Column(Integer, default=0)
    monthly_usage = Column(Integer, default=0)
    last_usage_reset = Column(DateTime(timezone=True), server_default=func.now())
    
    # Billing - Enhanced for Son1k payments
    stripe_customer_id = Column(String, nullable=True)
    subscription_status = Column(String, default="inactive")
    subscription_end_date = Column(DateTime(timezone=True), nullable=True)
    credits_remaining = Column(Integer, default=3)  # Monthly credits
    credits_used_this_month = Column(Integer, default=0)
    
    # Profile information
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    username = Column(String, unique=True, nullable=True)
    profile_image = Column(String, nullable=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)

class Job(Base):
    __tablename__ = "jobs"
    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=True)  # Allow anonymous for now
    
    # Core job data
    engine = Column(String, default="suno")
    prompt = Column(Text, nullable=True)
    lyrics = Column(Text, nullable=True)
    mode = Column(String, default="original")  # original | instrumental
    
    # Enhanced status tracking
    status = Column(String, default=JobStatus.QUEUED)
    priority = Column(Integer, default=0)  # Higher = more priority
    
    # Retry logic
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    next_retry_at = Column(DateTime(timezone=True), nullable=True)
    
    # Timing
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    assigned_at = Column(DateTime(timezone=True), nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    timeout_at = Column(DateTime(timezone=True), nullable=True)
    
    # Worker tracking
    worker_id = Column(String, nullable=True)  # Which extension worker took this job
    worker_heartbeat = Column(DateTime(timezone=True), nullable=True)
    
    # Error handling
    error_message = Column(Text, nullable=True)
    error_code = Column(String, nullable=True)
    error_screenshot_url = Column(String, nullable=True)
    
    # Results
    result_data = Column(JSON, nullable=True)  # Store Suno response data
    audio_url = Column(String, nullable=True)
    preview_url = Column(String, nullable=True)
    
    # Metadata
    source = Column(String, default="api")  # api | extension | frontend
    job_metadata = Column(JSON, nullable=True)  # Additional data

class Song(Base):
    __tablename__ = "songs"
    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"))
    job_id = Column(String, ForeignKey("jobs.id"))
    title = Column(String, nullable=True)
    emotion = Column(String, nullable=True)
    bpm = Column(Integer, nullable=True)
    key = Column(String, nullable=True)
    length_sec = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Asset(Base):
    __tablename__ = "assets"
    id = Column(String, primary_key=True)
    song_id = Column(String, ForeignKey("songs.id"))
    kind = Column(String)  # master | preview | stem_vocals | stem_drums ...
    url = Column(Text)
    size = Column(Integer, nullable=True)
    checksum = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Worker(Base):
    __tablename__ = "workers"
    id = Column(String, primary_key=True)  # Extension worker ID
    name = Column(String, nullable=True)
    status = Column(String, default="offline")  # online | offline | busy
    last_heartbeat = Column(DateTime(timezone=True), server_default=func.now())
    last_job_id = Column(String, nullable=True)
    version = Column(String, nullable=True)  # Extension version
    user_agent = Column(String, nullable=True)
    ip_address = Column(String, nullable=True)
    jobs_completed = Column(Integer, default=0)
    jobs_failed = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class UsageLog(Base):
    __tablename__ = "usage_logs"
    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"))
    job_id = Column(String, ForeignKey("jobs.id"))
    action = Column(String)  # generation | retry | cancel
    cost_credits = Column(Integer, default=1)  # Credits consumed
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    log_metadata = Column(JSON, nullable=True)

# Son1k Subscription Plans Configuration
SUBSCRIPTION_PLANS = {
    "free": {
        "name": "Plan Gratuito",
        "price": 0,
        "credits_per_month": 3,
        "max_duration": 60,  # segundos
        "daily_limit": 3,
        "concurrent_jobs": 1,
        "priority": 0,
        "features": ["3 canciones por mes", "Duración máxima 60s", "Calidad estándar"]
    },
    "basic": {
        "name": "Plan Básico", 
        "price": 9.99,
        "stripe_price_id": "price_basic_monthly",
        "credits_per_month": 50,
        "max_duration": 180,
        "daily_limit": 15,
        "concurrent_jobs": 2,
        "priority": 5,
        "features": ["50 canciones por mes", "Duración máxima 3min", "Calidad alta", "Sin marca de agua"]
    },
    "pro": {
        "name": "Plan Pro",
        "price": 19.99, 
        "stripe_price_id": "price_pro_monthly",
        "credits_per_month": 200,
        "max_duration": 300,
        "daily_limit": 50,
        "concurrent_jobs": 3,
        "priority": 10,
        "features": ["200 canciones por mes", "Duración máxima 5min", "Calidad premium", "Descarga en múltiples formatos", "Uso comercial"]
    },
    "unlimited": {
        "name": "Plan Ilimitado",
        "price": 49.99,
        "stripe_price_id": "price_unlimited_monthly", 
        "credits_per_month": -1,  # Ilimitado
        "max_duration": 600,
        "daily_limit": -1,
        "concurrent_jobs": 10,
        "priority": 20,
        "features": ["Canciones ilimitadas", "Duración máxima 10min", "Calidad premium", "Uso comercial", "API access", "Soporte prioritario"]
    }
}

# Backward compatibility
PLAN_LIMITS = {
    UserPlan.FREE: SUBSCRIPTION_PLANS["free"],
    UserPlan.PRO: SUBSCRIPTION_PLANS["pro"],
    UserPlan.ENTERPRISE: SUBSCRIPTION_PLANS["unlimited"]
}

# Pydantic models for API
class SongCreate(BaseModel):
    prompt: Optional[str] = None
    lyrics: Optional[str] = None
    mode: str = "original"  # original | instrumental
    title: Optional[str] = None
    emotion: Optional[str] = None
    bpm: Optional[int] = None
    key: Optional[str] = None
    length_sec: Optional[int] = 60

class JobResponse(BaseModel):
    id: str
    status: str
    created_at: datetime
    updated_at: datetime
    progress: Optional[str] = None
    error_message: Optional[str] = None
    audio_url: Optional[str] = None
    preview_url: Optional[str] = None

class UserQuota(BaseModel):
    plan: str
    daily_usage: int
    daily_limit: int
    monthly_usage: int
    monthly_limit: int
    concurrent_jobs: int
    can_create_job: bool

class WorkerHeartbeat(BaseModel):
    worker_id: str
    status: str
    version: Optional[str] = None
    current_job_id: Optional[str] = None
    jobs_completed: Optional[int] = 0
    jobs_failed: Optional[int] = 0

# Authentication Models
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    name: Optional[str] = None
    plan: str
    daily_usage: int
    daily_limit: int
    monthly_usage: int
    monthly_limit: int
    created_at: datetime
    
class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

# --- añade esto en models.py ---
from pydantic import BaseModel, Field
from typing import Optional, Literal

class GenerationRequest(BaseModel):
    prompt: str
    lyrics: Optional[str] = None
    instrumental: bool = False
    style: Optional[str] = None
    user_id: Optional[str] = None
    model: Optional[Literal["ghost", "studio", "cover", "remix", "default"]] = "default"
    duration: Optional[int] = Field(default=30, ge=5, le=300)
    seed: Optional[int] = None
    metadata: Optional[dict] = None

