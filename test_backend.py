import sys
import requests

print("Testing backend connectivity...")

try:
    # Test health endpoint
    response = requests.get("http://localhost:8001/health")
    print(f"\n✅ Health endpoint: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Test root endpoint
    response = requests.get("http://localhost:8001/")
    print(f"\n✅ Root endpoint: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Test login endpoint (should fail with 422 for missing data)
    response = requests.post("http://localhost:8001/api/auth/login", json={})
    print(f"\n📝 Login endpoint (empty): {response.status_code}")
    print(f"Response: {response.json()}")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
