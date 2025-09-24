#!/usr/bin/env python3
"""
Test script for Son1kVers3 system
"""

import requests
import json
import time

def test_system():
    """Test the Son1kVers3 system"""
    base_url = "http://localhost:8000"
    
    print("🎵 Testing Son1kVers3 System")
    print("=" * 40)
    
    # Test 1: Health check
    print("1. Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health check error: {e}")
    
    # Test 2: Frontend
    print("\n2. Testing frontend...")
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200 and "Son1kVers3" in response.text:
            print("✅ Frontend loaded successfully")
        else:
            print(f"❌ Frontend failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Frontend error: {e}")
    
    # Test 3: API status
    print("\n3. Testing API status...")
    try:
        response = requests.get(f"{base_url}/api/status", timeout=5)
        if response.status_code == 200:
            print("✅ API status check passed")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ API status failed: {response.status_code}")
    except Exception as e:
        print(f"❌ API status error: {e}")
    
    # Test 4: Tracks endpoint
    print("\n4. Testing tracks endpoint...")
    try:
        response = requests.get(f"{base_url}/api/tracks", timeout=5)
        if response.status_code == 200:
            print("✅ Tracks endpoint working")
            tracks = response.json()
            print(f"   Found {len(tracks.get('tracks', []))} tracks")
        else:
            print(f"❌ Tracks endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Tracks endpoint error: {e}")
    
    # Test 5: Music generation (mock test)
    print("\n5. Testing music generation...")
    try:
        # Test with a simple prompt
        payload = {
            "prompt": "test song",
            "style": "pop"
        }
        response = requests.post(
            f"{base_url}/api/generate", 
            json=payload, 
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Music generation endpoint working")
            print(f"   Status: {result.get('status')}")
            print(f"   Message: {result.get('message')}")
        else:
            print(f"❌ Music generation failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Music generation error: {e}")
    
    print("\n" + "=" * 40)
    print("🎵 System test completed!")

if __name__ == "__main__":
    test_system()

