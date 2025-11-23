#!/usr/bin/env python3
"""
Test script for Posts API endpoints.
Tests the complete posts functionality including creation, retrieval, likes, and deletion.
"""

import requests
import sys

# Configuration
BACKEND_URL = "http://127.0.0.1:8080"
TEST_USER = {
    "email": "admin@hiremebahamas.com",
    "password": "admin123"
}


def print_test(name, passed, details=""):
    """Print test result with formatting"""
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status}: {name}")
    if details:
        print(f"   {details}")
    print()


def test_health_check():
    """Test that backend is running"""
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        passed = response.status_code == 200
        print_test(
            "Health Check",
            passed,
            f"Status: {response.status_code}" if not passed else "Backend is healthy"
        )
        return passed
    except Exception as e:
        print_test("Health Check", False, f"Error: {str(e)}")
        return False


def test_login():
    """Test login and get token"""
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/auth/login",
            json=TEST_USER,
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            if token:
                print_test("Login", True, f"Token received")
                return token
            else:
                print_test("Login", False, "No token in response")
                return None
        else:
            print_test("Login", False, f"Status: {response.status_code}")
            return None
    except Exception as e:
        print_test("Login", False, f"Error: {str(e)}")
        return None


def test_create_post(token):
    """Test creating a new post"""
    try:
        post_data = {
            "content": "Test post from automated test script",
            "image_url": ""
        }
        
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.post(
            f"{BACKEND_URL}/api/posts",
            json=post_data,
            headers=headers,
            timeout=5
        )
        
        if response.status_code == 201:
            data = response.json()
            if data.get("success") and data.get("post"):
                post_id = data["post"]["id"]
                user = data["post"].get("user", {})
                print_test(
                    "Create Post",
                    True,
                    f"Post ID: {post_id}, Creator: {user.get('first_name', '')} {user.get('last_name', '')}"
                )
                return post_id
            else:
                print_test("Create Post", False, "Invalid response format")
                return None
        else:
            print_test("Create Post", False, f"Status: {response.status_code}, Response: {response.text}")
            return None
    except Exception as e:
        print_test("Create Post", False, f"Error: {str(e)}")
        return None


def test_get_posts(token):
    """Test retrieving all posts"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(
            f"{BACKEND_URL}/api/posts",
            headers=headers,
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            posts = data.get("posts", [])
            
            # Check if posts have required fields
            if posts:
                first_post = posts[0]
                required_fields = ["id", "content", "created_at", "likes_count", "user"]
                has_all_fields = all(field in first_post for field in required_fields)
                
                if has_all_fields:
                    # Check user information
                    user = first_post.get("user", {})
                    user_fields = ["id", "email", "first_name", "last_name"]
                    has_user_info = all(field in user for field in user_fields)
                    
                    print_test(
                        "Get Posts",
                        has_user_info,
                        f"Retrieved {len(posts)} post(s) with accurate user information"
                    )
                    return has_user_info
                else:
                    print_test("Get Posts", False, "Posts missing required fields")
                    return False
            else:
                print_test("Get Posts", True, "No posts found (empty database)")
                return True
        else:
            print_test("Get Posts", False, f"Status: {response.status_code}")
            return False
    except Exception as e:
        print_test("Get Posts", False, f"Error: {str(e)}")
        return False


def test_like_post(token, post_id):
    """Test liking a post"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.post(
            f"{BACKEND_URL}/api/posts/{post_id}/like",
            headers=headers,
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print_test(
                    "Like Post",
                    True,
                    f"Likes count: {data.get('likes_count', 0)}"
                )
                return True
            else:
                print_test("Like Post", False, "Success flag is False")
                return False
        else:
            print_test("Like Post", False, f"Status: {response.status_code}")
            return False
    except Exception as e:
        print_test("Like Post", False, f"Error: {str(e)}")
        return False


def test_unlike_post(token, post_id):
    """Test unliking a post"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.post(
            f"{BACKEND_URL}/api/posts/{post_id}/like",
            headers=headers,
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print_test(
                    "Unlike Post",
                    True,
                    f"Likes count: {data.get('likes_count', 0)}"
                )
                return True
            else:
                print_test("Unlike Post", False, "Success flag is False")
                return False
        else:
            print_test("Unlike Post", False, f"Status: {response.status_code}")
            return False
    except Exception as e:
        print_test("Unlike Post", False, f"Error: {str(e)}")
        return False


def test_delete_post(token, post_id):
    """Test deleting a post"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.delete(
            f"{BACKEND_URL}/api/posts/{post_id}",
            headers=headers,
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            passed = data.get("success", False)
            print_test("Delete Post", passed, "Post deleted successfully")
            return passed
        else:
            print_test("Delete Post", False, f"Status: {response.status_code}")
            return False
    except Exception as e:
        print_test("Delete Post", False, f"Error: {str(e)}")
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("Posts API Test Suite")
    print("=" * 60)
    print()
    
    # Test health check
    if not test_health_check():
        print("⚠️  Backend is not running. Please start it first:")
        print(f"   python final_backend_postgresql.py")
        sys.exit(1)
    
    # Test login
    token = test_login()
    if not token:
        print("⚠️  Login failed. Cannot continue tests.")
        sys.exit(1)
    
    # Test get posts (before creating any)
    test_get_posts(token)
    
    # Test create post
    post_id = test_create_post(token)
    if not post_id:
        print("⚠️  Post creation failed. Some tests will be skipped.")
        sys.exit(1)
    
    # Test get posts again (should include the new post)
    test_get_posts(token)
    
    # Test like post
    test_like_post(token, post_id)
    
    # Test unlike post
    test_unlike_post(token, post_id)
    
    # Test delete post
    test_delete_post(token, post_id)
    
    print("=" * 60)
    print("✅ All Posts API tests completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
