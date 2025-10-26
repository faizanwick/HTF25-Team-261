#!/usr/bin/env python3
"""
Test script to verify the voice API is working
"""
import requests
import json

def test_voice_api():
    base_url = "http://localhost:8000"
    
    print("🧪 Testing Voice API...")
    
    # Test 1: Check if server is running
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Server is running")
        else:
            print("❌ Server returned error:", response.status_code)
            return
    except requests.exceptions.ConnectionError:
        print("❌ Server is not running. Please start the server first.")
        print("   Run: python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
        return
    
    # Test 2: Test API key
    try:
        response = requests.get(f"{base_url}/voice/test-api", timeout=10)
        data = response.json()
        print(f"🔑 API Key Test: {data.get('status', 'unknown')}")
        if data.get('status') == 'success':
            print("✅ API key is working")
        else:
            print(f"⚠️  API key issue: {data.get('message', 'unknown error')}")
    except Exception as e:
        print(f"❌ API key test failed: {e}")
    
    # Test 3: Test voice command processing
    try:
        test_command = {
            "command": "create a simple function",
            "language": "python"
        }
        
        response = requests.post(
            f"{base_url}/voice/process", 
            json=test_command,
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"🎤 Voice Command Test: {data.get('status', 'unknown')}")
            print(f"📝 Response: {data.get('response', 'No response')}")
            if data.get('code_generated'):
                print(f"💻 Generated Code: {data.get('code_generated')}")
            print("✅ Voice command processing is working!")
        else:
            print(f"❌ Voice command test failed: {response.status_code}")
            print(f"   Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Voice command test failed: {e}")
    
    print("\n🎯 Test completed!")

if __name__ == "__main__":
    test_voice_api()
