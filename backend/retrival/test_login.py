"""Test login endpoint directly"""
import requests
import json
import time

# Give server time to start if needed
time.sleep(2)

try:
    url = "http://localhost:8000/api/v1/auth/login"
    data = {
        "email": "instructor@test.com",
        "password": "Instructor123!"
    }
    
    print(f"\nTesting login endpoint...")
    print(f"URL: {url}")
    print(f"Data: {json.dumps(data, indent=2)}\n")
    
    response = requests.post(url, json=data, timeout=10)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}\n")
    print(f"Response Body:\n{json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 200:
        print("\n✓ Login successful!")
    else:
        print(f"\n✗ Login failed with status {response.status_code}")
        
except requests.exceptions.ConnectionError as e:
    print(f"✗ Connection error: {e}")
    print("Make sure the backend server is running on port 8000")
except Exception as e:
    print(f"✗ Error: {e}")
