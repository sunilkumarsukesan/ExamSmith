"""
Debug script to test login endpoint directly.
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_login(email, password):
    """Test login endpoint."""
    url = f"{BASE_URL}/api/v1/auth/login"
    payload = {
        "email": email,
        "password": password
    }
    
    print(f"\n{'='*70}")
    print(f"Testing Login")
    print(f"{'='*70}")
    print(f"URL: {url}")
    print(f"Email: {email}")
    print(f"Password: {password}")
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        print(f"\nStatus Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"\nResponse Body:")
        print(json.dumps(response.json(), indent=2))
        
        if response.status_code == 200:
            print("\n✓ Login successful!")
            return True
        else:
            print(f"\n✗ Login failed with status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("\n✗ Connection error: Unable to connect to backend")
        print(f"  Make sure backend is running on {BASE_URL}")
        return False
    except requests.exceptions.Timeout:
        print("\n✗ Request timeout")
        return False
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        return False


def test_health():
    """Test health endpoint."""
    url = f"{BASE_URL}/health"
    
    print(f"\n{'='*70}")
    print(f"Testing Health Endpoint")
    print(f"{'='*70}")
    print(f"URL: {url}")
    
    try:
        response = requests.get(url, timeout=5)
        print(f"\nStatus Code: {response.status_code}")
        print(f"Response:")
        print(json.dumps(response.json(), indent=2))
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        print("\n✗ Connection error: Backend not accessible")
        return False
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        return False


if __name__ == "__main__":
    print("\n" + "="*70)
    print("ExamSmith API Debug Script")
    print("="*70)
    
    # Test health
    health_ok = test_health()
    
    if not health_ok:
        print("\n⚠ Backend is not responding. Make sure to run:")
        print("  npm run dev")
        exit(1)
    
    # Test login with all test users
    test_users = [
        ("admin@examsmith.com", "AdminPass123!"),
        ("instructor@test.com", "Instructor123!"),
        ("student@examsmith.com", "Student123!"),
    ]
    
    print("\n" + "="*70)
    print("Testing Login with All Test Users")
    print("="*70)
    
    for email, password in test_users:
        test_login(email, password)
    
    print("\n" + "="*70)
    print("Debug Complete")
    print("="*70 + "\n")
