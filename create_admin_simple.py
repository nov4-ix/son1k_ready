#!/usr/bin/env python3
# 👤 Son1kVers3 - Simple Admin User Creation
# Crear cuenta admin directamente

import sqlite3
import bcrypt
from datetime import datetime
import os

def create_admin_user():
    """Create admin user directly in database"""
    
    # User data
    email = "nov4-ix@son1kvers3.com"
    password = "iloveMusic!90"
    name = "Nov4-IX Admin"
    plan = "ENTERPRISE"
    
    print(f"🔑 Creating admin user: {email}")
    
    # Hash password with bcrypt
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password_bytes, salt).decode('utf-8')
    print("✅ Password hashed successfully")
    
    # Database path
    db_path = "son1k.db"
    if not os.path.exists(db_path):
        print("❌ Database not found. Run the backend first to create the database.")
        return False
    
    print(f"📁 Database path: {db_path}")
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        print("✅ Database connection established")
        
        # Check if user already exists
        cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
        existing_user = cursor.fetchone()
        
        if existing_user:
            print(f"⚠️  User {email} already exists. Updating...")
            
            # Update existing user
            cursor.execute("""
                UPDATE users 
                SET hashed_password = ?, 
                    plan = ?, 
                    updated_at = ?
                WHERE email = ?
            """, (hashed_password, plan, datetime.utcnow(), email))
            
        else:
            print(f"🆕 Creating new user: {email}")
            
            # Create new user - need to generate ID
            import uuid
            user_id = str(uuid.uuid4())
            
            cursor.execute("""
                INSERT INTO users (id, email, hashed_password, plan, is_active, daily_usage, monthly_usage, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id,
                email,
                hashed_password,
                plan,
                True,
                0,
                0,
                datetime.utcnow(),
                datetime.utcnow()
            ))
        
        # Commit changes
        conn.commit()
        print("✅ User created/updated successfully")
        
        # Verify user creation
        cursor.execute("SELECT id, email, plan, is_active FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()
        
        if user:
            print(f"✅ Verification successful:")
            print(f"   ID: {user[0]}")
            print(f"   Email: {user[1]}")
            print(f"   Plan: {user[2]}")
            print(f"   Active: {user[3]}")
        else:
            print("❌ Verification failed")
            return False
        
        conn.close()
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def show_all_users():
    """Show all users in database"""
    print("\n📊 All Users:")
    
    try:
        conn = sqlite3.connect("son1k.db")
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, email, plan, is_active, created_at FROM users ORDER BY created_at DESC")
        users = cursor.fetchall()
        
        if users:
            print("   Email | Plan | Active | Created")
            print("   " + "-" * 50)
            for user in users:
                print(f"   {user[1]} | {user[2]} | {user[3]} | {user[4]}")
        else:
            print("   No users found")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error showing users: {e}")

if __name__ == "__main__":
    print("👤 SON1KVERS3 - ADMIN USER CREATION")
    print("==================================")
    
    if create_admin_user():
        show_all_users()
        
        print("\n🎉 ADMIN USER SETUP COMPLETE!")
        print("============================")
        print("")
        print("👤 Admin Credentials:")
        print("   📧 Email: nov4-ix@son1kvers3.com")
        print("   🔐 Password: iloveMusic!90")
        print("   🎫 Plan: ENTERPRISE (unlimited songs)")
        print("")
        print("🔧 How to use:")
        print("   1. Go to http://localhost:8000 (local)")
        print("   2. Or https://son1kvers3.com (production)")
        print("   3. Click 'Login' button")
        print("   4. Use credentials above")
        print("   5. Generate unlimited music!")
        print("")
        print("✅ Ready for testing!")
        
    else:
        print("❌ Failed to create admin user")