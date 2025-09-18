#!/usr/bin/env python3
# 👥 Son1kVers3 - Create 50 Test User Accounts
# Crear 50 cuentas para testers

import sqlite3
import bcrypt
from datetime import datetime
import uuid
import random

def generate_test_users(count=50):
    """Generate test user accounts"""
    
    print(f"👥 Creating {count} test user accounts...")
    
    # Base data for users
    domains = ["gmail.com", "yahoo.com", "outlook.com", "hotmail.com", "test.com"]
    plans = ["FREE", "PRO", "ENTERPRISE"]
    plan_weights = [0.7, 0.25, 0.05]  # 70% FREE, 25% PRO, 5% ENTERPRISE
    
    # Common password for all test users
    password = "Test123!"
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password_bytes, salt).decode('utf-8')
    
    print("✅ Password hashed for all test users")
    
    # Connect to database
    try:
        conn = sqlite3.connect("son1k.db")
        cursor = conn.cursor()
        print("✅ Database connection established")
        
        users_created = 0
        test_users = []
        
        for i in range(1, count + 1):
            # Generate user data
            user_id = str(uuid.uuid4())
            email = f"tester{i:02d}@{random.choice(domains)}"
            plan = random.choices(plans, weights=plan_weights)[0]
            
            # Check if user already exists
            cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
            if cursor.fetchone():
                print(f"⚠️  User {email} already exists, skipping...")
                continue
            
            # Create user
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
            
            test_users.append({
                'email': email,
                'password': password,
                'plan': plan
            })
            
            users_created += 1
            
            if users_created % 10 == 0:
                print(f"✅ Created {users_created} test users...")
        
        # Commit all changes
        conn.commit()
        print(f"✅ Successfully created {users_created} test users")
        
        # Generate credentials file
        with open("test_users_credentials.txt", "w") as f:
            f.write("# Son1kVers3 Test User Credentials\n")
            f.write("# ================================\n")
            f.write(f"# Total Users: {users_created}\n")
            f.write(f"# Password for ALL: {password}\n")
            f.write("# \n")
            f.write("# Format: Email | Plan\n")
            f.write("# \n")
            
            # Group by plan
            for plan in plans:
                plan_users = [u for u in test_users if u['plan'] == plan]
                if plan_users:
                    f.write(f"\n## {plan} PLAN ({len(plan_users)} users):\n")
                    for user in plan_users:
                        f.write(f"{user['email']} | {user['plan']}\n")
        
        print("✅ Credentials saved to 'test_users_credentials.txt'")
        
        # Show statistics
        show_plan_stats(cursor)
        
        conn.close()
        return users_created
        
    except Exception as e:
        print(f"❌ Error creating test users: {e}")
        return 0

def show_plan_stats(cursor):
    """Show user statistics by plan"""
    print("\n📊 User Statistics by Plan:")
    
    cursor.execute("""
        SELECT plan, COUNT(*) as count 
        FROM users 
        GROUP BY plan 
        ORDER BY 
            CASE plan 
                WHEN 'FREE' THEN 1 
                WHEN 'PRO' THEN 2 
                WHEN 'ENTERPRISE' THEN 3 
                ELSE 4 
            END
    """)
    
    stats = cursor.fetchall()
    total = sum(count for _, count in stats)
    
    for plan, count in stats:
        percentage = (count / total) * 100
        print(f"   {plan:10s}: {count:3d} users ({percentage:4.1f}%)")
    
    print(f"   {'TOTAL':10s}: {total:3d} users")

def create_premium_testers():
    """Create specific premium test accounts"""
    print("\n🌟 Creating premium test accounts...")
    
    premium_accounts = [
        {"email": "premium.tester1@son1k.com", "plan": "ENTERPRISE"},
        {"email": "premium.tester2@son1k.com", "plan": "ENTERPRISE"},
        {"email": "pro.tester1@son1k.com", "plan": "PRO"},
        {"email": "pro.tester2@son1k.com", "plan": "PRO"},
        {"email": "pro.tester3@son1k.com", "plan": "PRO"},
    ]
    
    password = "Premium123!"
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password_bytes, salt).decode('utf-8')
    
    try:
        conn = sqlite3.connect("son1k.db")
        cursor = conn.cursor()
        
        for account in premium_accounts:
            user_id = str(uuid.uuid4())
            email = account["email"]
            plan = account["plan"]
            
            # Check if exists
            cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
            if cursor.fetchone():
                continue
            
            cursor.execute("""
                INSERT INTO users (id, email, hashed_password, plan, is_active, daily_usage, monthly_usage, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id, email, hashed_password, plan, True, 0, 0,
                datetime.utcnow(), datetime.utcnow()
            ))
            
            print(f"✅ Created premium account: {email} ({plan})")
        
        conn.commit()
        conn.close()
        
        # Save premium credentials
        with open("premium_testers.txt", "w") as f:
            f.write("# Son1kVers3 Premium Test Accounts\n")
            f.write("# ===============================\n")
            f.write(f"# Password for ALL: {password}\n")
            f.write("# \n")
            for account in premium_accounts:
                f.write(f"{account['email']} | {account['plan']}\n")
        
        print("✅ Premium credentials saved to 'premium_testers.txt'")
        
    except Exception as e:
        print(f"❌ Error creating premium accounts: {e}")

if __name__ == "__main__":
    print("👥 SON1KVERS3 - TEST USERS CREATION")
    print("==================================")
    
    # Create 50 random test users
    created = generate_test_users(50)
    
    # Create premium test accounts
    create_premium_testers()
    
    print(f"\n🎉 TEST USERS SETUP COMPLETE!")
    print("===========================")
    print("")
    print(f"👥 Regular Test Users: {created}")
    print("   📧 Format: tester01@domain.com to tester50@domain.com")
    print("   🔐 Password: Test123!")
    print("   📄 Full list: test_users_credentials.txt")
    print("")
    print("🌟 Premium Test Users: 5")
    print("   📧 premium.tester1@son1k.com, pro.tester1@son1k.com, etc.")
    print("   🔐 Password: Premium123!")
    print("   📄 Full list: premium_testers.txt")
    print("")
    print("🔧 How to use:")
    print("   1. Go to http://localhost:8000 or https://son1kvers3.com")
    print("   2. Click 'Login'")
    print("   3. Use any email from the files above")
    print("   4. Use corresponding password")
    print("   5. Test different plans and limits!")
    print("")
    print("📊 Plan Distribution:")
    print("   - FREE: ~70% (limited to 5 songs/day)")
    print("   - PRO: ~25% (limited to 50 songs/day)")
    print("   - ENTERPRISE: ~5% (unlimited songs)")
    print("")
    print("✅ Ready for testing with 55+ accounts!")