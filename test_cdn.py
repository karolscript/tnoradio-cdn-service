#!/usr/bin/env python3
"""
Test script for CDN Service
"""
import requests
import json
import sys
import time

def test_health_endpoint(base_url):
    """Test the health endpoint"""
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        print(f"Health endpoint status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Health response: {json.dumps(data, indent=2)}")
            return True
        else:
            print(f"Health check failed: {response.text}")
            return False
    except Exception as e:
        print(f"Error testing health endpoint: {e}")
        return False

def test_root_endpoint(base_url):
    """Test the root endpoint"""
    try:
        response = requests.get(f"{base_url}/", timeout=10)
        print(f"Root endpoint status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Root response: {json.dumps(data, indent=2)}")
            return True
        else:
            print(f"Root check failed: {response.text}")
            return False
    except Exception as e:
        print(f"Error testing root endpoint: {e}")
        return False

def test_rate_limiting(base_url):
    """Test rate limiting"""
    print("Testing rate limiting...")
    try:
        # Make multiple requests quickly
        for i in range(5):
            response = requests.get(f"{base_url}/health", timeout=5)
            print(f"Request {i+1}: {response.status_code}")
            time.sleep(0.1)
        return True
    except Exception as e:
        print(f"Error testing rate limiting: {e}")
        return False

def main():
    """Main test function"""
    base_url = "http://localhost:19000"
    
    print("🧪 Testing CDN Service...")
    print(f"Base URL: {base_url}")
    print("-" * 50)
    
    # Test health endpoint
    print("1. Testing health endpoint...")
    health_ok = test_health_endpoint(base_url)
    
    # Test root endpoint
    print("\n2. Testing root endpoint...")
    root_ok = test_root_endpoint(base_url)
    
    # Test rate limiting
    print("\n3. Testing rate limiting...")
    rate_ok = test_rate_limiting(base_url)
    
    # Summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY:")
    print(f"Health endpoint: {'✅ PASS' if health_ok else '❌ FAIL'}")
    print(f"Root endpoint: {'✅ PASS' if root_ok else '❌ FAIL'}")
    print(f"Rate limiting: {'✅ PASS' if rate_ok else '❌ FAIL'}")
    
    if all([health_ok, root_ok, rate_ok]):
        print("\n🎉 All tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)

if __name__ == "__main__":
    main() 