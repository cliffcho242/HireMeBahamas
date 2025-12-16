#!/usr/bin/env python3
"""
Test mobile optimization features: pagination and N+1 query prevention
"""

def test_pagination_limits():
    """Test that pagination limits are correctly set to max 50"""
    import ast
    import re
    from pathlib import Path
    
    api_dir = Path(__file__).parent / "api" / "backend_app" / "api"
    
    # Files to check
    files_to_check = [
        "jobs.py",
        "posts.py", 
        "users.py",
        "notifications.py",
        "messages.py",
        "reviews.py",
    ]
    
    print("Testing pagination limits (max 50 for mobile optimization)...")
    all_pass = True
    
    for filename in files_to_check:
        filepath = api_dir / filename
        if not filepath.exists():
            print(f"  ❌ File not found: {filename}")
            all_pass = False
            continue
            
        content = filepath.read_text()
        
        # Find all Query parameters with limit
        # Pattern: limit: int = Query(..., ge=1, le=X)
        pattern = r'limit:\s*int\s*=\s*Query\([^)]*le=(\d+)[^)]*\)'
        matches = re.findall(pattern, content)
        
        if not matches:
            print(f"  ⚠️  No pagination found in {filename}")
            continue
        
        # Check all limits are <= 50
        file_pass = True
        for limit in matches:
            limit_val = int(limit)
            if limit_val > 50:
                print(f"  ❌ {filename}: limit={limit_val} exceeds mobile-friendly max of 50")
                file_pass = False
                all_pass = False
        
        if file_pass:
            print(f"  ✅ {filename}: All pagination limits ≤ 50 (found {len(matches)} endpoints)")
    
    return all_pass


def test_no_n_plus_one_in_users_list():
    """Test that users list endpoint doesn't have N+1 queries"""
    from pathlib import Path
    
    filepath = Path(__file__).parent / "api" / "backend_app" / "api" / "users.py"
    content = filepath.read_text()
    
    print("\nTesting users list endpoint for N+1 query prevention...")
    
    # Look for the get_users function
    if "def get_users(" not in content:
        print("  ❌ get_users function not found")
        return False
    
    # Extract the function body
    func_start = content.find("def get_users(")
    # Find the next function definition
    next_func = content.find("\n@router.", func_start + 1)
    if next_func == -1:
        next_func = content.find("\ndef ", func_start + 100)
    
    func_body = content[func_start:next_func] if next_func > 0 else content[func_start:]
    
    # Check for bulk loading patterns (good)
    has_bulk_followers = "select(Follow.followed_id, func.count()" in func_body
    has_bulk_following = "select(Follow.follower_id, func.count()" in func_body
    has_group_by = ".group_by(Follow." in func_body
    
    # Check for individual query patterns (bad)
    has_individual_queries = func_body.count("for user in users:") > 0 and \
                            func_body.count("await db.execute") > 4  # More than 4 queries in loop
    
    if has_bulk_followers and has_bulk_following and has_group_by:
        print("  ✅ Bulk loading follower/following counts (no N+1)")
        return True
    else:
        print("  ❌ Missing bulk loading patterns for follower/following counts")
        if not has_bulk_followers:
            print("    - Missing bulk followers count query")
        if not has_bulk_following:
            print("    - Missing bulk following count query")
        if not has_group_by:
            print("    - Missing group_by for aggregation")
        return False


def test_jobs_count_query_efficiency():
    """Test that jobs endpoint uses efficient count query"""
    from pathlib import Path
    
    filepath = Path(__file__).parent / "api" / "backend_app" / "api" / "jobs.py"
    content = filepath.read_text()
    
    print("\nTesting jobs endpoint for efficient count query...")
    
    # Look for the get_jobs function
    if "def get_jobs(" not in content:
        print("  ❌ get_jobs function not found")
        return False
    
    # Extract the function body
    func_start = content.find("def get_jobs(")
    next_func = content.find("\n@router.", func_start + 1)
    if next_func == -1:
        next_func = content.find("\ndef ", func_start + 100)
    
    func_body = content[func_start:next_func] if next_func > 0 else content[func_start:]
    
    # Check for efficient count (good)
    has_func_count = "select(func.count())" in func_body
    
    # Check for inefficient count (bad)
    has_inefficient_count = "len(count_result.all())" in func_body or \
                           "len(result.all())" in func_body
    
    if has_func_count and not has_inefficient_count:
        print("  ✅ Using func.count() for efficient counting")
        return True
    elif has_inefficient_count:
        print("  ❌ Using inefficient len(result.all()) for counting")
        return False
    else:
        print("  ⚠️  Count query pattern not clearly identified")
        return False


def main():
    """Run all mobile optimization tests"""
    print("=" * 60)
    print("MOBILE OPTIMIZATION TEST SUITE")
    print("=" * 60)
    
    results = []
    
    # Test 1: Pagination limits
    results.append(("Pagination Limits", test_pagination_limits()))
    
    # Test 2: N+1 prevention in users list
    results.append(("Users List N+1 Prevention", test_no_n_plus_one_in_users_list()))
    
    # Test 3: Jobs count query efficiency
    results.append(("Jobs Count Query Efficiency", test_jobs_count_query_efficiency()))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nPassed: {passed}/{total}")
    
    if passed == total:
        print("\n✅ All mobile optimization tests passed!")
        return 0
    else:
        print(f"\n❌ {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    exit(main())
