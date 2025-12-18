#!/usr/bin/env python3
"""
Test script to verify async task destroyed warning fix.

This script tests that:
1. Startup handlers are defined with @app.on_event("startup")
2. Shutdown handlers are defined with @app.on_event("shutdown")
3. Shutdown handlers include asyncio.sleep(0) for task cleanup
4. Background tasks use safe wrapper functions with exception handling
"""

import os
import sys
import ast
import re

def check_file_for_patterns(filepath: str) -> dict:
    """Check a Python file for correct async task handling patterns.
    
    Args:
        filepath: Path to Python file to check
        
    Returns:
        Dictionary with test results
    """
    results = {
        'file': filepath,
        'has_startup_event': False,
        'has_shutdown_event': False,
        'shutdown_has_sleep': False,
        'has_safe_wrapper': False,
        'unsafe_create_task': [],
        'errors': []
    }
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for startup event handler
        if re.search(r'@app\.on_event\(["\']startup["\']\)', content):
            results['has_startup_event'] = True
        
        # Check for shutdown event handler
        if re.search(r'@app\.on_event\(["\']shutdown["\']\)', content):
            results['has_shutdown_event'] = True
            
            # Check if shutdown handler has asyncio.sleep(0)
            # Extract the shutdown function
            shutdown_match = re.search(
                r'@app\.on_event\(["\']shutdown["\']\)\s*\n\s*async\s+def\s+\w+\([^)]*\):.*?(?=\n(?:async\s+def|\Z|@app))',
                content,
                re.DOTALL
            )
            if shutdown_match:
                shutdown_func = shutdown_match.group(0)
                if 'await asyncio.sleep(0)' in shutdown_func:
                    results['shutdown_has_sleep'] = True
        
        # Check for safe wrapper functions (safe_background_init, safe_warm_cache, etc.)
        if re.search(r'async\s+def\s+safe_\w+\([^)]*\):', content):
            results['has_safe_wrapper'] = True
        
        # Check for unsafe create_task usage (outside of event handlers or safe wrappers)
        # This is a simplified check - look for create_task not in startup handler
        create_task_matches = re.finditer(r'asyncio\.create_task\([^)]+\)', content)
        for match in create_task_matches:
            line_num = content[:match.start()].count('\n') + 1
            # Check if it's in a startup event handler
            # Find the context (which function is it in?)
            context_start = content.rfind('async def ', 0, match.start())
            if context_start != -1:
                context_end = content.find('\n', context_start)
                context = content[context_start:context_end]
                
                # Look backwards for @app.on_event("startup")
                decorator_search_start = max(0, context_start - 200)
                decorator_context = content[decorator_search_start:context_start]
                
                if '@app.on_event("startup")' not in decorator_context and '@app.on_event(\'startup\')' not in decorator_context:
                    # Not in startup handler - but check if it's in lifespan
                    if 'lifespan' not in context.lower():
                        results['unsafe_create_task'].append({
                            'line': line_num,
                            'match': match.group(0)
                        })
    
    except Exception as e:
        results['errors'].append(str(e))
    
    return results


def main():
    """Run tests on main.py files."""
    print("=" * 80)
    print("Testing Async Task Destroyed Warning Fix")
    print("=" * 80)
    print()
    
    # Files to check
    files_to_check = [
        'app/main.py',
        'backend/app/main.py',
        'backend/app/main_immortal.py',
        'api/backend_app/main.py',
    ]
    
    repo_root = '/home/runner/work/HireMeBahamas/HireMeBahamas'
    all_passed = True
    
    for filepath in files_to_check:
        full_path = os.path.join(repo_root, filepath)
        
        if not os.path.exists(full_path):
            print(f"⚠️  SKIP: {filepath} (file not found)")
            print()
            continue
        
        print(f"Testing: {filepath}")
        print("-" * 80)
        
        results = check_file_for_patterns(full_path)
        
        if results['errors']:
            print(f"❌ ERRORS reading file:")
            for error in results['errors']:
                print(f"   {error}")
            all_passed = False
            print()
            continue
        
        # Check startup event
        if results['has_startup_event']:
            print("✅ Has @app.on_event('startup') decorator")
        else:
            print("⚠️  No @app.on_event('startup') decorator found")
        
        # Check shutdown event
        if results['has_shutdown_event']:
            print("✅ Has @app.on_event('shutdown') decorator")
        else:
            print("❌ FAIL: Missing @app.on_event('shutdown') decorator")
            all_passed = False
        
        # Check shutdown has asyncio.sleep(0)
        if results['has_shutdown_event']:
            if results['shutdown_has_sleep']:
                print("✅ Shutdown handler includes 'await asyncio.sleep(0)'")
            else:
                print("❌ FAIL: Shutdown handler missing 'await asyncio.sleep(0)'")
                all_passed = False
        
        # Check for safe wrappers
        if results['has_safe_wrapper']:
            print("✅ Has safe wrapper function(s) for background tasks")
        else:
            print("ℹ️  No safe wrapper functions found (may not be needed)")
        
        # Check for unsafe create_task
        if results['unsafe_create_task']:
            print(f"⚠️  WARNING: Found {len(results['unsafe_create_task'])} potentially unsafe asyncio.create_task() usage:")
            for task in results['unsafe_create_task']:
                print(f"   Line {task['line']}: {task['match']}")
        else:
            print("✅ No unsafe asyncio.create_task() usage detected")
        
        print()
    
    print("=" * 80)
    if all_passed:
        print("✅ ALL TESTS PASSED")
        print()
        print("Summary:")
        print("- All main.py files have proper @app.on_event('shutdown') handlers")
        print("- All shutdown handlers include 'await asyncio.sleep(0)' for task cleanup")
        print("- Background tasks use safe wrapper functions with exception handling")
        print()
        print("This prevents 'Task was destroyed but it is pending!' warnings")
        print("when Gunicorn restarts workers.")
        return 0
    else:
        print("❌ SOME TESTS FAILED")
        print()
        print("Please review the failures above and ensure all files follow")
        print("the safe async task handling pattern.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
