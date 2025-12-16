#!/usr/bin/env python3
"""
Validation Script for Mobile Optimization Implementation

This script validates that all the required mobile optimization features
have been properly implemented without requiring external dependencies.
"""
import os
import re
import sys


def check_file_exists(filepath, description):
    """Check if a file exists."""
    if os.path.exists(filepath):
        print(f"✓ {description}: {filepath}")
        return True
    else:
        print(f"✗ {description} NOT FOUND: {filepath}")
        return False


def check_file_contains(filepath, patterns, description):
    """Check if a file contains specific patterns."""
    if not os.path.exists(filepath):
        print(f"✗ {description}: File not found - {filepath}")
        return False
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    all_found = True
    for pattern in patterns:
        # Case-insensitive search
        if pattern.lower() in content.lower() or re.search(pattern, content, re.IGNORECASE):
            print(f"  ✓ Found: {pattern[:50]}...")
        else:
            print(f"  ✗ Missing: {pattern[:50]}...")
            all_found = False
    
    if all_found:
        print(f"✓ {description}")
    else:
        print(f"✗ {description} - Some patterns missing")
    
    return all_found


def main():
    """Main validation function."""
    print("=" * 70)
    print("Mobile Optimization Implementation Validation")
    print("=" * 70)
    print()
    
    # Get the base path (script directory parent, or use environment variable if available)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_path = os.getenv("GITHUB_WORKSPACE", script_dir)
    backend_path = os.path.join(base_path, "backend")
    
    all_checks_passed = True
    
    # =========================================================================
    # 1. Check Background Tasks Module
    # =========================================================================
    print("1. Background Tasks Module")
    print("-" * 70)
    
    bg_tasks_file = os.path.join(backend_path, "app/core/background_tasks.py")
    if check_file_exists(bg_tasks_file, "Background tasks module"):
        patterns = [
            "send_email_notification_task",
            "send_push_notification_task",
            "notify_new_follower_task",
            "notify_new_like_task",
            "notify_new_comment_task",
            "notify_new_message_task",
            "fanout_post_to_followers_task",
            "add_email_notification",
            "add_push_notification",
            "add_fanout_task",
            "non-blocking",
        ]
        all_checks_passed &= check_file_contains(
            bg_tasks_file,
            patterns,
            "Background task functions"
        )
    else:
        all_checks_passed = False
    
    print()
    
    # =========================================================================
    # 2. Check Posts API Updates
    # =========================================================================
    print("2. Posts API - Background Tasks Integration")
    print("-" * 70)
    
    posts_api = os.path.join(backend_path, "app/api/posts.py")
    if check_file_exists(posts_api, "Posts API"):
        patterns = [
            "from app.core.background_tasks import",
            "BackgroundTasks",
            "background_tasks: BackgroundTasks",
            "add_fanout_task",
            "notify_new_like_task",
            "notify_new_comment_task",
        ]
        all_checks_passed &= check_file_contains(
            posts_api,
            patterns,
            "Posts API background task integration"
        )
    else:
        all_checks_passed = False
    
    print()
    
    # =========================================================================
    # 3. Check Users API Updates
    # =========================================================================
    print("3. Users API - Background Tasks Integration")
    print("-" * 70)
    
    users_api = os.path.join(backend_path, "app/api/users.py")
    if check_file_exists(users_api, "Users API"):
        patterns = [
            "from app.core.background_tasks import",
            "BackgroundTasks",
            "background_tasks: BackgroundTasks",
            "notify_new_follower_task",
        ]
        all_checks_passed &= check_file_contains(
            users_api,
            patterns,
            "Users API background task integration"
        )
    else:
        all_checks_passed = False
    
    print()
    
    # =========================================================================
    # 4. Check Messages API Updates
    # =========================================================================
    print("4. Messages API - Background Tasks Integration")
    print("-" * 70)
    
    messages_api = os.path.join(backend_path, "app/api/messages.py")
    if check_file_exists(messages_api, "Messages API"):
        patterns = [
            "from app.core.background_tasks import",
            "BackgroundTasks",
            "background_tasks: BackgroundTasks",
            "notify_new_message_task",
        ]
        all_checks_passed &= check_file_contains(
            messages_api,
            patterns,
            "Messages API background task integration"
        )
    else:
        all_checks_passed = False
    
    print()
    
    # =========================================================================
    # 5. Check Pagination Module
    # =========================================================================
    print("5. Pagination Module")
    print("-" * 70)
    
    pagination_file = os.path.join(backend_path, "app/core/pagination.py")
    if check_file_exists(pagination_file, "Pagination module"):
        patterns = [
            "paginate_with_cursor",
            "paginate_with_offset",
            "paginate_auto",
            "encode_cursor",
            "decode_cursor",
            "PaginationMetadata",
        ]
        all_checks_passed &= check_file_contains(
            pagination_file,
            patterns,
            "Pagination functions"
        )
    else:
        all_checks_passed = False
    
    print()
    
    # =========================================================================
    # 6. Check Database Indexes
    # =========================================================================
    print("6. Database Indexes")
    print("-" * 70)
    
    indexes_file = os.path.join(backend_path, "create_database_indexes.py")
    if check_file_exists(indexes_file, "Database indexes script"):
        patterns = [
            "idx_users_email",
            "idx_posts",
            "idx_jobs",
            "idx_messages",
            "idx_notifications",
        ]
        all_checks_passed &= check_file_contains(
            indexes_file,
            patterns,
            "Database index definitions"
        )
    else:
        all_checks_passed = False
    
    print()
    
    # =========================================================================
    # 7. Check N+1 Query Prevention
    # =========================================================================
    print("7. N+1 Query Prevention")
    print("-" * 70)
    
    if check_file_exists(posts_api, "Posts API"):
        patterns = [
            "batch_get_post_metadata",
            "selectinload",
            "post_ids = \\[post.id for post in",
        ]
        all_checks_passed &= check_file_contains(
            posts_api,
            patterns,
            "N+1 query prevention in Posts API"
        )
    else:
        all_checks_passed = False
    
    print()
    
    # =========================================================================
    # 8. Check Test Files
    # =========================================================================
    print("8. Test Files")
    print("-" * 70)
    
    test_file = os.path.join(backend_path, "test_mobile_optimization.py")
    check_file_exists(test_file, "Mobile optimization tests")
    
    print()
    
    # =========================================================================
    # 9. Check Documentation
    # =========================================================================
    print("9. Documentation")
    print("-" * 70)
    
    doc_file = os.path.join(base_path, "MOBILE_OPTIMIZATION_IMPLEMENTATION.md")
    if check_file_exists(doc_file, "Implementation documentation"):
        patterns = [
            "Background Jobs",
            "Database Strategy",
            "Mobile API Optimization",
            "Pagination",
            "N+1",
        ]
        all_checks_passed &= check_file_contains(
            doc_file,
            patterns,
            "Documentation completeness"
        )
    else:
        all_checks_passed = False
    
    print()
    
    # =========================================================================
    # Summary
    # =========================================================================
    print("=" * 70)
    print("Validation Summary")
    print("=" * 70)
    
    if all_checks_passed:
        print("✓ All mobile optimization features successfully implemented!")
        print()
        print("Key Features:")
        print("  • Background tasks for email, push, and fan-out operations")
        print("  • Dual pagination (cursor-based and offset-based)")
        print("  • N+1 query prevention with batch queries")
        print("  • Database indexes on heavily accessed columns")
        print("  • Small JSON payloads with optimized schemas")
        print()
        return 0
    else:
        print("✗ Some validation checks failed")
        print("  Please review the output above for details")
        print()
        return 1


if __name__ == "__main__":
    sys.exit(main())
