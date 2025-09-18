#!/usr/bin/env python3
"""
Initialize database with user tables for Son1kVers3 commercial launch
"""
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.app.db import init_db, engine
from backend.app.models import Base

if __name__ == "__main__":
    print("🚀 Initializing Son1kVers3 Commercial Database...")
    
    # Create all tables
    init_db()
    
    print("✅ Database initialized successfully!")
    print("📊 Tables created:")
    print("   - users (authentication & plans)")
    print("   - jobs (music generation queue)")
    print("   - songs (generated music)")
    print("   - assets (audio files)")
    print("   - workers (extension workers)")
    print("   - usage_logs (billing & analytics)")
    
    print("\n🎯 Ready for commercial launch!")
    print("   • Users can register/login")
    print("   • Rate limiting by plan (FREE/PRO/ENTERPRISE)")
    print("   • Automatic worker processing")
    print("   • Usage tracking and quotas")