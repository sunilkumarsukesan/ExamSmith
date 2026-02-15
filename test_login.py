"""Quick test for login endpoint"""
import requests
import json

try:
    response = requests.post(
        'http://localhost:8000/api/v1/auth/login',
        json={
            'email': 'admin@examsmith.com',
            'password': 'admin123'
        },
        timeout=5
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response:")
    print(json.dumps(response.json(), indent=2))
    
    if response.status_code == 200:
        print("\n✓ Login SUCCESS!")
    else:
        print(f"\n✗ Login FAILED with status {response.status_code}")
        
except requests.exceptions.ConnectionError:
    print("✗ Cannot connect to backend at http://localhost:8000")
    print("Make sure the backend is running")
except Exception as e:
    print(f"✗ Error: {e}")
