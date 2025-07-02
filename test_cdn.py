#!/usr/bin/env python3
"""
Test script for CDN service endpoints
"""

import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration - Update this to your VPS IP
BASE_URL = "http://82.25.79.43:19000"  # VPS IP address

def test_health():
    """Test the health endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Health check: {response.status_code}")
        print(f"Response: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"Health check failed: {e}")
        return False

def test_get_videos():
    """Test the get_videos endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/get_videos?collection=trailers")
        print(f"Get videos: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response keys: {list(data.keys())}")
            print(f"Total items: {data.get('totalItems', 'N/A')}")
            print(f"Items count: {len(data.get('items', []))}")
        else:
            print(f"Error response: {response.text}")
        
        return response.status_code == 200
    except Exception as e:
        print(f"Get videos failed: {e}")
        return False

def test_get_stream():
    """Test the get_stream endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/get_stream")
        print(f"Get stream: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response keys: {list(data.keys())}")
        else:
            print(f"Error response: {response.text}")
        
        return response.status_code == 200
    except Exception as e:
        print(f"Get stream failed: {e}")
        return False

def test_cors():
    """Test CORS headers"""
    try:
        headers = {
            'Origin': 'http://localhost:3000',
            'Access-Control-Request-Method': 'GET',
            'Access-Control-Request-Headers': 'Content-Type'
        }
        
        # Test preflight request
        response = requests.options(f"{BASE_URL}/get_videos", headers=headers)
        print(f"CORS preflight: {response.status_code}")
        print(f"Access-Control-Allow-Origin: {response.headers.get('Access-Control-Allow-Origin', 'Not set')}")
        print(f"Access-Control-Allow-Methods: {response.headers.get('Access-Control-Allow-Methods', 'Not set')}")
        
        return response.status_code == 200
    except Exception as e:
        print(f"CORS test failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing CDN Service on VPS (82.25.79.43)...")
    print("=" * 50)
    
    # Test health endpoint
    print("\n1. Testing health endpoint:")
    health_ok = test_health()
    
    # Test CORS
    print("\n2. Testing CORS configuration:")
    cors_ok = test_cors()
    
    # Test get_videos endpoint
    print("\n3. Testing get_videos endpoint:")
    videos_ok = test_get_videos()
    
    # Test get_stream endpoint
    print("\n4. Testing get_stream endpoint:")
    stream_ok = test_get_stream()
    
    print("\n" + "=" * 50)
    print("Test Results:")
    print(f"Health: {'✅ PASS' if health_ok else '❌ FAIL'}")
    print(f"CORS: {'✅ PASS' if cors_ok else '❌ FAIL'}")
    print(f"Get Videos: {'✅ PASS' if videos_ok else '❌ FAIL'}")
    print(f"Get Stream: {'✅ PASS' if stream_ok else '❌ FAIL'}")
    
    if all([health_ok, cors_ok, videos_ok, stream_ok]):
        print("\n🎉 All tests passed! CDN service is working correctly.")
    else:
        print("\n⚠️  Some tests failed. Check the service configuration.") 