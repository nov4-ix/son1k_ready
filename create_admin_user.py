#!/usr/bin/env python3
# 👤 Son1kVers3 - Create Admin User Script
# Crear cuenta admin para pruebas y administración

import os
import sys
import sqlite3
from datetime import datetime

# Agregar el directorio backend al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

try:
    from app.auth import hash_password
    from app.db import get_db_path
    print("✅ Imports successful")
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running from the project root directory")
    sys.exit(1)

def create_admin_user():
    """Create admin user for Son1kVers3"""
    
    # User data
    email = "nov4-ix@son1kvers3.com"
    password = "iloveMusic!90"
    name = "Nov4-IX Admin"
    plan = "ENTERPRISE"  # Admin gets enterprise plan
    
    print(f"🔑 Creating admin user: {email}")
    
    # Hash password
    hashed_password = hash_password(password)
    print("✅ Password hashed successfully")
    
    # Get database path
    db_path = get_db_path()
    print(f"📁 Database path: {db_path}")
    
    # Connect to database
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        print("✅ Database connection established")
        
        # Check if user already exists
        cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
        existing_user = cursor.fetchone()
        
        if existing_user:
            print(f"⚠️  User {email} already exists. Updating password...")
            
            # Update existing user
            cursor.execute("""
                UPDATE users 
                SET password_hash = ?, 
                    name = ?, 
                    plan = ?, 
                    updated_at = ?
                WHERE email = ?
            """, (hashed_password, name, plan, datetime.utcnow(), email))
            
        else:
            print(f"🆕 Creating new user: {email}")
            
            # Create new user
            cursor.execute("""
                INSERT INTO users (email, password_hash, name, plan, is_active, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                email,
                hashed_password,
                name,
                plan,
                True,
                datetime.utcnow(),
                datetime.utcnow()
            ))
        
        # Commit changes
        conn.commit()
        print("✅ User created/updated successfully")
        
        # Verify user creation
        cursor.execute("SELECT id, email, name, plan, is_active FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()
        
        if user:
            print(f"✅ Verification successful:")
            print(f"   ID: {user[0]}")
            print(f"   Email: {user[1]}")
            print(f"   Name: {user[2]}")
            print(f"   Plan: {user[3]}")
            print(f"   Active: {user[4]}")
        else:
            print("❌ Verification failed - user not found")
        
        conn.close()
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False
    
    return True

def test_login():
    """Test login with created user"""
    print("\n🧪 Testing login...")
    
    try:
        from app.auth import authenticate_user
        
        email = "nov4-ix@son1kvers3.com"
        password = "iloveMusic!90"
        
        user = authenticate_user(email, password)
        
        if user:
            print("✅ Login test successful!")
            print(f"   User ID: {user.id}")
            print(f"   Email: {user.email}")
            print(f"   Name: {user.name}")
            print(f"   Plan: {user.plan}")
        else:
            print("❌ Login test failed - authentication failed")
            
    except Exception as e:
        print(f"❌ Login test error: {e}")

def show_user_stats():
    """Show statistics of all users"""
    print("\n📊 User Statistics:")
    
    try:
        db_path = get_db_path()
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Count users by plan
        cursor.execute("""
            SELECT plan, COUNT(*) as count 
            FROM users 
            GROUP BY plan
        """)
        plans = cursor.fetchall()
        
        print("   Users by plan:")
        for plan, count in plans:
            print(f"     {plan}: {count} users")
        
        # Total users
        cursor.execute("SELECT COUNT(*) FROM users")
        total = cursor.fetchone()[0]
        print(f"   Total users: {total}")
        
        # Recent users
        cursor.execute("""
            SELECT email, name, plan, created_at 
            FROM users 
            ORDER BY created_at DESC 
            LIMIT 5
        """)
        recent = cursor.fetchall()
        
        print("   Recent users:")
        for email, name, plan, created_at in recent:
            print(f"     {email} ({plan}) - {created_at}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Statistics error: {e}")

if __name__ == "__main__":
    print("👤 SON1KVERS3 - ADMIN USER CREATION")
    print("==================================")
    
    # Create admin user
    if create_admin_user():
        # Test login
        test_login()
        
        # Show stats
        show_user_stats()
        
        print("\n🎉 ADMIN USER SETUP COMPLETE!")
        print("============================")
        print("")
        print("👤 Admin Credentials:")
        print("   Email: nov4-ix@son1kvers3.com")
        print("   Password: iloveMusic!90")
        print("   Plan: ENTERPRISE (unlimited)")
        print("")
        print("🔧 Usage:")
        print("   1. Go to https://son1kvers3.com")
        print("   2. Click 'Login'")
        print("   3. Use the credentials above")
        print("   4. Enjoy unlimited music generation!")
        print("")
        print("💡 For local testing:")
        print("   Visit: http://localhost:8000")
        print("   Same credentials work")
        
    else:
        print("❌ Admin user creation failed")
        sys.exit(1)