#!/usr/bin/env python3
"""
Test script for the Tothu API
Tests basic functionality of all endpoints
"""

import requests
import json
import os
from pathlib import Path

BASE_URL = "http://localhost:8001"

def test_health():
    """Test health endpoint"""
    print("\n=== Testing Health Endpoint ===")
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_register():
    """Test user registration"""
    print("\n=== Testing User Registration ===")
    try:
        random_id = os.urandom(4).hex()
        data = {
            "email": f"test{random_id}@example.com",
            "username": f"testuser{random_id}",
            "full_name": f"Test User {random_id}",
            "password": "testpassword123"
        }
        response = requests.post(f"{BASE_URL}/api/auth/register", json=data)
        print(f"Status: {response.status_code}")
        result = response.json()
        if 'access_token' in result:
            print(f"Response: User registered successfully with token")
        else:
            print(f"Response: {result}")
        return response.status_code == 201
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_models():
    """Test model info endpoint"""
    print("\n=== Testing Model Info Endpoint ===")
    try:
        response = requests.get(f"{BASE_URL}/api/chat/model-info")
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Model info: {json.dumps(data, indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_image_validation():
    """Test image validation endpoint (demo mode)"""
    print("\n=== Testing Image Validation (Demo Mode) ===")
    try:
        data = {
            "document_type": "invoice"
        }
        response = requests.post(f"{BASE_URL}/api/image-validation/validate-demo", data=data)
        print(f"Status: {response.status_code}")
        result = response.json()
        if response.status_code == 200:
            print(f"Validation successful: {result.get('status', 'N/A')}")
            print(f"Document type: {result.get('document_type', 'N/A')}")
        else:
            print(f"Validation result: {json.dumps(result, indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("TOTHU API TEST SUITE")
    print("=" * 60)
    
    results = {
        "Health Check": test_health(),
        "User Registration": test_register(),
        "Models List": test_models(),
        "Image Validation (Demo)": test_image_validation(),
    }
    
    print("\n" + "=" * 60)
    print("TEST RESULTS SUMMARY")
    print("=" * 60)
    
    for test_name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{test_name:30} {status}")
    
    total = len(results)
    passed = sum(results.values())
    print(f"\nTotal: {passed}/{total} tests passed")
    
    return all(results.values())

if __name__ == "__main__":
    import sys
    sys.exit(0 if main() else 1)
