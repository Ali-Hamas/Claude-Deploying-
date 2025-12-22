import requests
import json

# Test backend /api/chat endpoint
BASE_URL = "http://127.0.0.1:8000"

print("Testing Todo Chat Backend...")
print("=" * 50)

# Step 1: Register a test user (or login)
print("\n1. Testing registration...")
try:
    register_response = requests.post(
        f"{BASE_URL}/auth/register",
        json={
            "email": "testchat@example.com",
            "password": "testchat123",
            "name": "Test Chat User"
        }
    )
    print(f"Register Status: {register_response.status_code}")
    if register_response.ok:
        register_data = register_response.json()
        token = register_data.get("access_token")
        print(f"✓ Got access token: {token[:20]}...")
    else:
        # Try login if user exists
        print("User exists, trying login...")
        login_response = requests.post(
            f"{BASE_URL}/auth/login",
            json={
                "email": "testchat@example.com",
                "password": "testchat123"
            }
        )
        print(f"Login Status: {login_response.status_code}")
        if login_response.ok:
            login_data = login_response.json()
            token = login_data.get("access_token")
            print(f"✓ Got access token: {token[:20]}...")
        else:
            print(f"✗ Login failed: {login_response.text}")
            exit(1)
except Exception as e:
    print(f"✗ Error: {e}")
    exit(1)

# Step 2: Test /api/chat endpoint
print("\n2. Testing /api/chat endpoint...")
try:
    chat_response = requests.post(
        f"{BASE_URL}/api/chat",
        json={
            "message": "Hello, list my tasks",
            "conversation_id": None
        },
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    )
    print(f"Chat Status: {chat_response.status_code}")
    if chat_response.ok:
        chat_data = chat_response.json()
        print(f"✓ Response: {chat_data.get('response')}")
        print(f"✓ Conversation ID: {chat_data.get('conversation_id')}")
    else:
        print(f"✗ Error: {chat_response.text}")
        print(f"✗ Status code: {chat_response.status_code}")
except Exception as e:
    print(f"✗ Connection Error: {e}")
    print("\nPossible causes:")
    print("- Backend is not running on port 8000")
    print("- CORS is blocking the request")
    print("- Network/firewall issue")

print("\n" + "=" * 50)
print("Test complete!")
