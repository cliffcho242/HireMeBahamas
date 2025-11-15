#!/usr/bin/env python3
"""
Comprehensive test for message functionality with multiple users
"""

import json
import sys

from final_backend import app

print("Testing complete message flow with user isolation...")
print("=" * 60)

with app.test_client() as client:
    # Login as user 1
    print("\n1. Logging in as User 1:")
    login1 = client.post(
        "/api/auth/login",
        data=json.dumps({"email": "testuser1@example.com", "password": "TestPass123!"}),
        content_type="application/json"
    )
    user1_data = login1.get_json()
    user1_token = user1_data.get("access_token")
    user1_id = user1_data.get("user", {}).get("id")
    user1_headers = {"Authorization": f"Bearer {user1_token}"}
    print(f"   ✓ User 1 logged in, ID: {user1_id}")

    # Login as user 2
    print("\n2. Logging in as User 2:")
    login2 = client.post(
        "/api/auth/login",
        data=json.dumps({"email": "testuser2@example.com", "password": "TestPass123!"}),
        content_type="application/json"
    )
    user2_data = login2.get_json()
    user2_token = user2_data.get("access_token")
    user2_id = user2_data.get("user", {}).get("id")
    user2_headers = {"Authorization": f"Bearer {user2_token}"}
    print(f"   ✓ User 2 logged in, ID: {user2_id}")

    # User 1 creates a conversation with User 2
    print(f"\n3. User 1 creating conversation with User 2:")
    conv_response = client.post(
        "/api/messages/conversations",
        data=json.dumps({"participant_id": user2_id}),
        content_type="application/json",
        headers=user1_headers
    )
    conv_data = conv_response.get_json()
    conversation_id = conv_data.get("id")
    print(f"   Status: {conv_response.status_code}")
    print(f"   ✓ Conversation created, ID: {conversation_id}")
    assert conv_data["participant_1_id"] == user1_id, "User 1 should be participant 1"
    assert conv_data["participant_2_id"] == user2_id, "User 2 should be participant 2"
    print(f"   ✓ Participants verified")

    # User 1 sends a message
    print(f"\n4. User 1 sending message in conversation:")
    msg1_response = client.post(
        "/api/messages/",
        data=json.dumps({
            "conversation_id": conversation_id,
            "content": "Hello from User 1!"
        }),
        content_type="application/json",
        headers=user1_headers
    )
    msg1_data = msg1_response.get_json()
    print(f"   Status: {msg1_response.status_code}")
    print(f"   ✓ Message sent, ID: {msg1_data.get('id')}")
    assert msg1_data["sender_id"] == user1_id, "Sender should be User 1"
    assert msg1_data["content"] == "Hello from User 1!", "Content should match"

    # User 2 gets conversations - should see the conversation with User 1
    print(f"\n5. User 2 fetching conversations:")
    user2_convs = client.get("/api/messages/conversations", headers=user2_headers)
    user2_convs_data = user2_convs.get_json()
    print(f"   Status: {user2_convs.status_code}")
    print(f"   ✓ Found {len(user2_convs_data)} conversation(s)")
    assert len(user2_convs_data) == 1, "User 2 should see 1 conversation"
    assert user2_convs_data[0]["id"] == conversation_id, "Should be the same conversation"
    assert len(user2_convs_data[0]["messages"]) == 1, "Should have 1 message"
    print(f"   ✓ Conversation verified, has {len(user2_convs_data[0]['messages'])} message(s)")

    # User 2 sends a reply
    print(f"\n6. User 2 replying in conversation:")
    msg2_response = client.post(
        "/api/messages/",
        data=json.dumps({
            "conversation_id": conversation_id,
            "content": "Hello from User 2! Nice to meet you."
        }),
        content_type="application/json",
        headers=user2_headers
    )
    msg2_data = msg2_response.get_json()
    print(f"   Status: {msg2_response.status_code}")
    print(f"   ✓ Reply sent, ID: {msg2_data.get('id')}")
    assert msg2_data["sender_id"] == user2_id, "Sender should be User 2"

    # User 1 gets conversations - should see updated conversation
    print(f"\n7. User 1 fetching conversations again:")
    user1_convs = client.get("/api/messages/conversations", headers=user1_headers)
    user1_convs_data = user1_convs.get_json()
    print(f"   Status: {user1_convs.status_code}")
    print(f"   ✓ Found {len(user1_convs_data)} conversation(s)")
    assert len(user1_convs_data) == 1, "User 1 should see 1 conversation"
    assert len(user1_convs_data[0]["messages"]) == 2, "Should have 2 messages now"
    print(f"   ✓ Conversation has {len(user1_convs_data[0]['messages'])} messages")

    # Verify message order and content
    messages = user1_convs_data[0]["messages"]
    assert messages[0]["sender_id"] == user1_id, "First message from User 1"
    assert messages[1]["sender_id"] == user2_id, "Second message from User 2"
    print(f"   ✓ Message order and senders verified")

    # Test isolation: User 2 should NOT be able to send message with fake conversation_id
    print(f"\n8. Testing isolation - User 2 tries fake conversation ID:")
    fake_conv_id = 99999
    fake_msg_response = client.post(
        "/api/messages/",
        data=json.dumps({
            "conversation_id": fake_conv_id,
            "content": "This should fail"
        }),
        content_type="application/json",
        headers=user2_headers
    )
    print(f"   Status: {fake_msg_response.status_code}")
    assert fake_msg_response.status_code == 404, "Should not find fake conversation"
    print(f"   ✓ Correctly rejects message to non-existent conversation")

    # Test duplicate conversation creation
    print(f"\n9. Testing duplicate conversation prevention:")
    dup_conv_response = client.post(
        "/api/messages/conversations",
        data=json.dumps({"participant_id": user2_id}),
        content_type="application/json",
        headers=user1_headers
    )
    dup_conv_data = dup_conv_response.get_json()
    print(f"   Status: {dup_conv_response.status_code}")
    assert dup_conv_data["id"] == conversation_id, "Should return existing conversation"
    print(f"   ✓ Returns existing conversation instead of creating duplicate")

    # Test reverse direction (User 2 creates conversation with User 1)
    print(f"\n10. Testing reverse conversation creation:")
    rev_conv_response = client.post(
        "/api/messages/conversations",
        data=json.dumps({"participant_id": user1_id}),
        content_type="application/json",
        headers=user2_headers
    )
    rev_conv_data = rev_conv_response.get_json()
    print(f"   Status: {rev_conv_response.status_code}")
    assert rev_conv_data["id"] == conversation_id, "Should return same conversation"
    print(f"   ✓ Bidirectional conversation detection works")

print("\n" + "=" * 60)
print("✅ All comprehensive message tests passed!")
print("=" * 60)
print("\n📊 Summary:")
print("  - User authentication and isolation: ✓")
print("  - Conversation creation and deduplication: ✓")
print("  - Message sending and receiving: ✓")
print("  - Proper user filtering: ✓")
print("  - Security validation: ✓")
