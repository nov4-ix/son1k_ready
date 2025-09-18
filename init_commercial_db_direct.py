#!/usr/bin/env python3
"""
Initialize commercial database with enhanced tables
"""

import os
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

from backend.app.db import engine, Base
from backend.app.models import User, Job, Song, Asset, Worker, UsageLog, UserPlan
from datetime import datetime
import uuid

def init_commercial_db():
    """Initialize database with commercial tables"""
    print("🏗️  Creating commercial database tables...")
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully")
    
    # Create sample users for testing
    from sqlalchemy.orm import sessionmaker
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Check if demo users exist
        existing_user = session.query(User).filter(User.email == "demo@son1k.com").first()
        if not existing_user:
            print("👤 Creating demo users...")
            
            # Free user
            free_user = User(
                id=str(uuid.uuid4()),
                email="demo@son1k.com",
                plan=UserPlan.FREE,
                daily_usage=0,
                monthly_usage=0,
                is_active=True,
                created_at=datetime.utcnow()
            )
            
            # Pro user
            pro_user = User(
                id=str(uuid.uuid4()),
                email="pro@son1k.com", 
                plan=UserPlan.PRO,
                daily_usage=5,
                monthly_usage=45,
                subscription_status="active",
                is_active=True,
                created_at=datetime.utcnow()
            )
            
            # Enterprise user
            enterprise_user = User(
                id=str(uuid.uuid4()),
                email="enterprise@son1k.com",
                plan=UserPlan.ENTERPRISE,
                daily_usage=0,
                monthly_usage=0,
                subscription_status="active",
                is_active=True,
                created_at=datetime.utcnow()
            )
            
            session.add_all([free_user, pro_user, enterprise_user])
            session.commit()
            
            print(f"✅ Created demo users:")
            print(f"   📧 Free: demo@son1k.com (ID: {free_user.id})")
            print(f"   💎 Pro: pro@son1k.com (ID: {pro_user.id})")
            print(f"   🏢 Enterprise: enterprise@son1k.com (ID: {enterprise_user.id})")
        else:
            print("👤 Demo users already exist")
            
    except Exception as e:
        print(f"❌ Error creating demo users: {e}")
        session.rollback()
    finally:
        session.close()
    
    print("🎯 Commercial database initialization complete!")
    print("\n📋 Available endpoints:")
    print("   🔹 POST /api/songs/create - Create job with quota checking")
    print("   🔹 GET /api/jobs/{job_id} - Get job status")
    print("   🔹 POST /api/jobs/{job_id}/retry - Retry failed job") 
    print("   🔹 GET /api/users/{user_id}/quota - Check user quota")
    print("   🔹 GET /api/worker/jobs/next - Worker polling")
    print("   🔹 POST /api/worker/heartbeat - Worker heartbeat")
    print("   🔹 POST /api/jobs/{job_id}/update - Update job status")

if __name__ == "__main__":
    init_commercial_db()