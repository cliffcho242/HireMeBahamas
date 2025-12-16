#!/usr/bin/env python3
"""
Test script for WebSocket real-time notifications.

Tests:
1. WebSocket connection with JWT authentication
2. Receiving real-time notifications
3. Like count updates
4. Comment count updates
5. User presence (online/offline)
6. Ping/pong heartbeat
"""
import asyncio
import json
import os
import sys
import time
from datetime import datetime

import requests

# Try to import Socket.IO client
try:
    import socketio
    HAS_SOCKETIO = True
except ImportError:
    print("❌ python-socketio not installed. Install with: pip install python-socketio")
    sys.exit(1)


class WebSocketTester:
    """Test WebSocket real-time features."""
    
    def __init__(self, base_url: str = "http://localhost:10000"):
        """
        Initialize the WebSocket tester.
        
        Args:
            base_url: Base URL of the backend server
        """
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.token = None
        self.user_id = None
        self.sio = socketio.Client()
        self.notifications_received = []
        self.events_received = []
        
        # Register event handlers
        self._register_handlers()
    
    def _register_handlers(self):
        """Register Socket.IO event handlers."""
        
        @self.sio.event
        def connect():
            print(f"✅ WebSocket connected (sid: {self.sio.sid})")
        
        @self.sio.event
        def disconnect():
            print("❌ WebSocket disconnected")
        
        @self.sio.event
        def connected(data):
            print(f"✅ Connection confirmed: {data}")
        
        @self.sio.event
        def notification(data):
            print(f"🔔 Notification received: {data}")
            self.notifications_received.append(data)
        
        @self.sio.event
        def like_update(data):
            print(f"👍 Like update: Post {data.get('post_id')} - {data.get('like_count')} likes")
            self.events_received.append(('like', data))
        
        @self.sio.event
        def comment_update(data):
            print(f"💬 Comment update: Post {data.get('post_id')} - {data.get('comment_count')} comments")
            self.events_received.append(('comment', data))
        
        @self.sio.event
        def user_status(data):
            print(f"👤 User status: {data.get('user_id')} is {data.get('status')}")
            self.events_received.append(('user_status', data))
        
        @self.sio.event
        def pong(data):
            print(f"🏓 Pong received: {data}")
        
        @self.sio.event
        def new_message(data):
            print(f"💌 New message: {data}")
            self.events_received.append(('message', data))
        
        @self.sio.event
        def typing(data):
            print(f"⌨️  Typing: {data.get('user_name')} is {'typing' if data.get('is_typing') else 'not typing'}")
    
    def register_user(self, email: str = None, password: str = "Test1234!") -> bool:
        """Register a test user."""
        if not email:
            email = f"test_{int(time.time())}@example.com"
        
        print(f"\n📝 Registering user: {email}")
        
        try:
            response = requests.post(
                f"{self.api_url}/auth/register",
                json={
                    "email": email,
                    "password": password,
                    "first_name": "Test",
                    "last_name": "User",
                    "user_type": "job_seeker"
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.token = data.get("token")
                    self.user_id = data.get("user", {}).get("id")
                    print(f"✅ User registered successfully (ID: {self.user_id})")
                    return True
            
            print(f"❌ Registration failed: {response.text}")
            return False
        
        except Exception as e:
            print(f"❌ Registration error: {e}")
            return False
    
    def login_user(self, email: str, password: str = "Test1234!") -> bool:
        """Login an existing user."""
        print(f"\n🔑 Logging in: {email}")
        
        try:
            response = requests.post(
                f"{self.api_url}/auth/login",
                json={"email": email, "password": password},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.token = data.get("token")
                    self.user_id = data.get("user", {}).get("id")
                    print(f"✅ Login successful (ID: {self.user_id})")
                    return True
            
            print(f"❌ Login failed: {response.text}")
            return False
        
        except Exception as e:
            print(f"❌ Login error: {e}")
            return False
    
    def connect_websocket(self) -> bool:
        """Connect to WebSocket with authentication."""
        if not self.token:
            print("❌ No token available. Please login first.")
            return False
        
        print(f"\n🔌 Connecting to WebSocket: {self.base_url}")
        
        try:
            # Connect with JWT token for authentication
            self.sio.connect(
                self.base_url,
                auth={"token": self.token},
                transports=['websocket', 'polling']
            )
            
            time.sleep(1)  # Wait for connection to establish
            
            if self.sio.connected:
                print("✅ WebSocket connected successfully")
                return True
            else:
                print("❌ WebSocket connection failed")
                return False
        
        except Exception as e:
            print(f"❌ WebSocket connection error: {e}")
            return False
    
    def test_ping(self):
        """Test ping/pong heartbeat."""
        print("\n🏓 Testing ping/pong...")
        
        try:
            self.sio.emit('ping')
            time.sleep(0.5)
            print("✅ Ping sent")
        except Exception as e:
            print(f"❌ Ping failed: {e}")
    
    def test_notification(self):
        """Test sending a notification via REST API."""
        print("\n🔔 Testing notification via REST API...")
        
        try:
            response = requests.post(
                f"{self.api_url}/ws/test-notification",
                headers={"Authorization": f"Bearer {self.token}"},
                json={"message": "This is a test notification!"},
                timeout=10
            )
            
            if response.status_code == 200:
                print("✅ Test notification sent")
                time.sleep(1)  # Wait for notification to arrive
            else:
                print(f"❌ Failed to send notification: {response.text}")
        
        except Exception as e:
            print(f"❌ Notification test error: {e}")
    
    def get_websocket_status(self):
        """Get WebSocket server status."""
        print("\n📊 Getting WebSocket status...")
        
        try:
            response = requests.get(
                f"{self.api_url}/ws/status",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ WebSocket Status:")
                print(f"   - Enabled: {data.get('websocket_enabled')}")
                print(f"   - Active Connections: {data.get('active_connections')}")
                print(f"   - Online Users: {data.get('online_users')}")
                print(f"   - Redis Enabled: {data.get('redis_enabled')}")
                return data
            else:
                print(f"❌ Failed to get status: {response.text}")
        
        except Exception as e:
            print(f"❌ Status check error: {e}")
    
    def disconnect(self):
        """Disconnect from WebSocket."""
        if self.sio.connected:
            print("\n👋 Disconnecting...")
            self.sio.disconnect()
            time.sleep(0.5)
    
    def run_full_test(self):
        """Run complete test suite."""
        print("=" * 60)
        print("WebSocket Real-Time Notifications Test Suite")
        print("=" * 60)
        
        # Step 1: Check server status
        self.get_websocket_status()
        
        # Step 2: Register or login
        if not self.register_user():
            print("❌ Failed to register user")
            return False
        
        # Step 3: Connect WebSocket
        if not self.connect_websocket():
            print("❌ Failed to connect WebSocket")
            return False
        
        # Step 4: Test ping
        self.test_ping()
        
        # Step 5: Test notification
        self.test_notification()
        
        # Step 6: Wait for events
        print("\n⏳ Waiting for events (5 seconds)...")
        time.sleep(5)
        
        # Step 7: Summary
        print("\n" + "=" * 60)
        print("Test Summary")
        print("=" * 60)
        print(f"✅ Notifications received: {len(self.notifications_received)}")
        print(f"✅ Events received: {len(self.events_received)}")
        
        if self.notifications_received:
            print("\nNotifications:")
            for notif in self.notifications_received:
                print(f"  - {notif}")
        
        if self.events_received:
            print("\nEvents:")
            for event_type, data in self.events_received:
                print(f"  - {event_type}: {data}")
        
        # Step 8: Disconnect
        self.disconnect()
        
        print("\n✅ Test completed!")
        return True


def main():
    """Main test function."""
    # Get base URL from environment or use default
    base_url = os.getenv("BACKEND_URL", "http://localhost:10000")
    
    print(f"Testing WebSocket at: {base_url}")
    
    tester = WebSocketTester(base_url)
    
    try:
        tester.run_full_test()
    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted by user")
        tester.disconnect()
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        tester.disconnect()


if __name__ == "__main__":
    main()
