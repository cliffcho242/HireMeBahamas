#!/usr/bin/env python3
"""
Test message endpoints with proper user isolation
"""

import json
import sys

from final_backend import app

print("Testing message endpoints with user isolation...")
print("=" * 60)

with app.test_client() as client:
    # Test 1: Try to access conversations without authentication
    print("\n1. Testing GET /api/messages/conversations without auth (should fail):")
    response = client.get("/api/messages/conversations")
    print(f"   Status: {response.status_code}")
    result = response.get_json()
    print(f"   Message: {result.get('message')}")
    assert response.status_code == 401, "Should require authentication"
    print("   ✓ Correctly requires authentication")

    # Test 2: Login as test user 1
    print("\n2. Logging in as test user 1:")
    login_data = {"email": "testuser1@example.com", "password": "TestPass123!"}
    login_response = client.post(
        "/api/auth/login", 
        data=json.dumps(login_data), 
        content_type="application/json"
    )
    
    if login_response.status_code != 200:
        print(f"   ✗ Login failed: {login_response.get_json()}")
        sys.exit(1)
    
    login_result = login_response.get_json()
    if not login_result.get("success"):
        print(f"   ✗ Login failed: {login_result.get('message')}")
        sys.exit(1)
    
    token = login_result.get("access_token")
    user_id = login_result.get("user", {}).get("id")
    print(f"   Status: {login_response.status_code}")
    print(f"   ✓ Login successful, user_id: {user_id}")
    
    headers = {"Authorization": f"Bearer {token}"}

    # Test 3: Get conversations with authentication
    print("\n3. Testing GET /api/messages/conversations with auth:")
    response = client.get("/api/messages/conversations", headers=headers)
    print(f"   Status: {response.status_code}")
    conversations = response.get_json()
    print(f"   ✓ Conversations retrieved: {len(conversations)} conversations")
    
    # Verify all conversations involve the authenticated user
    if conversations:
        for conv in conversations:
            assert (
                conv["participant_1_id"] == user_id or 
                conv["participant_2_id"] == user_id
            ), f"Conversation {conv['id']} doesn't involve user {user_id}!"
        print(f"   ✓ All conversations properly filtered for user {user_id}")
    else:
        print("   ✓ Empty conversations list (no messages yet)")

    # Test 4: Try to send message without conversation_id
    print("\n4. Testing POST /api/messages/ without conversation_id (should fail):")
    message_data = {"content": "Test message"}
    response = client.post(
        "/api/messages/",
        data=json.dumps(message_data),
        content_type="application/json",
        headers=headers
    )
    print(f"   Status: {response.status_code}")
    result = response.get_json()
    print(f"   Message: {result.get('message')}")
    assert response.status_code == 400, "Should reject message without conversation_id"
    print("   ✓ Correctly validates required fields")

    # Test 5: Try to access conversations without Bearer prefix
    print("\n5. Testing with malformed auth header (should fail):")
    bad_headers = {"Authorization": token}  # Missing "Bearer " prefix
    response = client.get("/api/messages/conversations", headers=bad_headers)
    print(f"   Status: {response.status_code}")
    assert response.status_code == 401, "Should reject malformed auth header"
    print("   ✓ Correctly rejects malformed auth headers")

    # Test 6: Create conversation with invalid participant
    print("\n6. Testing POST /api/messages/conversations without participant_id (should fail):")
    conv_data = {}
    response = client.post(
        "/api/messages/conversations",
        data=json.dumps(conv_data),
        content_type="application/json",
        headers=headers
    )
    print(f"   Status: {response.status_code}")
    result = response.get_json()
    print(f"   Message: {result.get('message')}")
    assert response.status_code == 400, "Should require participant_id"
    print("   ✓ Correctly validates conversation creation")

    # Test 7: Try to create conversation with self
    print("\n7. Testing POST /api/messages/conversations with self (should fail):")
    conv_data = {"participant_id": user_id}
    response = client.post(
        "/api/messages/conversations",
        data=json.dumps(conv_data),
        content_type="application/json",
        headers=headers
    )
    print(f"   Status: {response.status_code}")
    result = response.get_json()
    print(f"   Message: {result.get('message')}")
    assert response.status_code == 400, "Should not allow conversation with self"
    print("   ✓ Correctly prevents self-conversations")

print("\n" + "=" * 60)
print("✅ All message endpoint tests passed!")
print("=" * 60)
