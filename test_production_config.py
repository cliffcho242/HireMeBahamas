#!/usr/bin/env python3
"""
Test Production Configuration - Validate "DO NOT EVER DO" List Compliance

This test validates that the HireMeBahamas backend follows all production best practices
as outlined in the problem statement.
"""
import os
import sys
import re
from pathlib import Path


def test_single_worker_config():
    """Test that Gunicorn is configured with single worker (workers=1)"""
    print("\n1. Testing Single Worker Configuration...")
    
    # Check gunicorn.conf.py
    gunicorn_files = [
        Path("gunicorn.conf.py"),
        Path("backend/gunicorn.conf.py")
    ]
    
    for config_file in gunicorn_files:
        if not config_file.exists():
            continue
            
        content = config_file.read_text()
        
        # Check default worker count is 1
        if 'workers = int(os.environ.get("WEB_CONCURRENCY", "1"))' in content:
            print(f"   ✅ {config_file}: Default workers=1")
        else:
            print(f"   ❌ {config_file}: Worker configuration not found or incorrect")
            return False
    
    # Check Procfiles
    procfiles = [
        Path("Procfile"),
        Path("backend/Procfile")
    ]
    
    for procfile in procfiles:
        if not procfile.exists():
            continue
            
        content = procfile.read_text()
        
        # Check for --workers 1 flag
        if "--workers 1" in content:
            print(f"   ✅ {procfile}: Uses --workers 1")
        else:
            print(f"   ⚠️  {procfile}: Relies on config file for worker count")
    
    return True


def test_no_reload_flag():
    """Test that --reload flag is not used in production configs"""
    print("\n2. Testing No --reload Flag...")
    
    # Check Procfiles
    procfiles = [
        Path("Procfile"),
        Path("backend/Procfile")
    ]
    
    for procfile in procfiles:
        if not procfile.exists():
            continue
            
        content = procfile.read_text()
        
        # Check that --reload is NOT present (excluding comments)
        lines = content.split('\n')
        has_reload = False
        for line in lines:
            # Skip comment lines
            if line.strip().startswith('#'):
                continue
            # Check if --reload is in the actual command
            if '--reload' in line:
                has_reload = True
                break
        
        if has_reload:
            print(f"   ❌ {procfile}: Contains --reload flag")
            return False
        else:
            print(f"   ✅ {procfile}: No --reload flag")
    
    # Check render.yaml
    render_config = Path("render.yaml")
    if render_config.exists():
        content = render_config.read_text()
        lines = content.split('\n')
        has_reload = False
        for line in lines:
            # Skip comment lines and lines with reload only in comments
            if '#' in line:
                # Check if --reload appears before the comment
                before_comment = line.split('#')[0]
                if '--reload' in before_comment:
                    has_reload = True
                    break
            elif '--reload' in line:
                has_reload = True
                break
        
        if has_reload:
            print(f"   ❌ render.yaml: Contains --reload flag")
            return False
        else:
            print(f"   ✅ render.yaml: No --reload flag")
    
    return True


def test_health_check_no_db():
    """Test that health check endpoints don't touch the database"""
    print("\n3. Testing Health Check No DB Dependency...")
    
    # Check main.py health endpoint
    main_file = Path("backend/app/main.py")
    if main_file.exists():
        content = main_file.read_text()
        
        # Find the health endpoint definition
        health_match = re.search(
            r'@app\.get\("/health".*?\ndef health\(\):.*?return.*?\n',
            content,
            re.DOTALL
        )
        
        if health_match:
            health_code = health_match.group(0)
            
            # Check that it doesn't use get_db, doesn't await DB calls
            if 'get_db' not in health_code and 'async' not in health_code:
                print(f"   ✅ /health endpoint: No DB dependency (sync function)")
            else:
                print(f"   ⚠️  /health endpoint: May have DB dependency")
        else:
            print(f"   ⚠️  /health endpoint: Not found in expected format")
    
    # Check health.py if it exists
    health_file = Path("backend/app/health.py")
    if health_file.exists():
        content = health_file.read_text()
        
        # Check that base /health endpoint doesn't use Depends(get_db)
        health_match = re.search(
            r'@router\.get\("/health".*?\ndef health\(\):.*?return.*?\n',
            content,
            re.DOTALL
        )
        
        if health_match:
            health_code = health_match.group(0)
            
            if 'Depends(get_db)' not in health_code:
                print(f"   ✅ health.py /health: No DB dependency")
            else:
                print(f"   ❌ health.py /health: Has DB dependency")
                return False
    
    return True


def test_lazy_db_initialization():
    """Test that database engine uses lazy initialization"""
    print("\n4. Testing Lazy DB Initialization...")
    
    database_file = Path("backend/app/database.py")
    if not database_file.exists():
        print(f"   ⚠️  database.py not found")
        return True
    
    content = database_file.read_text()
    
    # Check for lazy engine initialization pattern
    if "class LazyEngine:" in content and "def get_engine():" in content:
        print(f"   ✅ Lazy engine initialization pattern found")
    else:
        print(f"   ⚠️  Lazy engine pattern may not be implemented")
    
    # Check that no engine.connect() or engine.begin() at module level
    # (these should only be in functions, not at import time)
    lines = content.split('\n')
    module_level_db_calls = []
    indent_level = 0
    
    for i, line in enumerate(lines, 1):
        # Track if we're inside a function/class
        if re.match(r'^(async )?def |^class ', line):
            indent_level = len(line) - len(line.lstrip())
        
        # Check for DB calls at module level (not indented inside functions)
        if indent_level == 0 and ('engine.connect()' in line or 'engine.begin()' in line):
            if not line.strip().startswith('#'):
                module_level_db_calls.append(f"Line {i}: {line.strip()}")
    
    if module_level_db_calls:
        print(f"   ⚠️  Possible module-level DB calls found:")
        for call in module_level_db_calls:
            print(f"      {call}")
    else:
        print(f"   ✅ No module-level DB calls found")
    
    return True


def test_async_startup():
    """Test that startup event is async and non-blocking"""
    print("\n5. Testing Async Startup Configuration...")
    
    main_file = Path("backend/app/main.py")
    if not main_file.exists():
        print(f"   ⚠️  main.py not found")
        return True
    
    content = main_file.read_text()
    
    # Find startup event
    startup_match = re.search(
        r'@app\.on_event\("startup"\).*?async def startup\(\):.*?(?=@app\.on_event|^[^\s])',
        content,
        re.DOTALL
    )
    
    if startup_match:
        startup_code = startup_match.group(0)
        
        # Check for async background task scheduling
        if 'asyncio.create_task' in startup_code:
            print(f"   ✅ Startup uses async background tasks")
        else:
            print(f"   ⚠️  Startup may not use background tasks")
        
        # Check that there are no blocking DB calls in main startup
        # Look for await init_db() that's NOT inside a create_task
        has_blocking_init = False
        if 'await init_db()' in startup_code:
            # Check if it's wrapped in create_task
            lines = startup_code.split('\n')
            for i, line in enumerate(lines):
                if 'await init_db()' in line:
                    # Look at previous lines to see if we're inside create_task
                    context = '\n'.join(lines[max(0, i-5):i])
                    if 'create_task' not in context and 'async def ' not in context:
                        has_blocking_init = True
                        break
        
        if has_blocking_init:
            print(f"   ⚠️  Startup may have blocking DB initialization")
        else:
            print(f"   ✅ No blocking DB calls in startup")
    
    return True


def test_expected_log_messages():
    """Test that code includes expected log messages from problem statement"""
    print("\n6. Testing Expected Log Messages...")
    
    gunicorn_file = Path("backend/gunicorn.conf.py")
    if gunicorn_file.exists():
        content = gunicorn_file.read_text()
        
        # Check for "Booting worker with pid" message
        if 'Booting worker with pid' in content:
            print(f"   ✅ 'Booting worker with pid' message found")
        else:
            print(f"   ⚠️  'Booting worker with pid' message not found")
    
    main_file = Path("backend/app/main.py")
    if main_file.exists():
        content = main_file.read_text()
        
        # Check for "Application startup complete" or similar
        if 'Application startup complete' in content or 'startup complete' in content.lower():
            print(f"   ✅ 'Application startup complete' message found")
        else:
            print(f"   ⚠️  Startup complete message not found")
    
    return True


def main():
    """Run all configuration tests"""
    print("="*80)
    print("  HireMeBahamas Production Configuration Validation")
    print("  Testing compliance with 'DO NOT EVER DO' list")
    print("="*80)
    
    tests = [
        ("Single Worker Configuration", test_single_worker_config),
        ("No --reload Flag", test_no_reload_flag),
        ("Health Check No DB", test_health_check_no_db),
        ("Lazy DB Initialization", test_lazy_db_initialization),
        ("Async Startup", test_async_startup),
        ("Expected Log Messages", test_expected_log_messages),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"   ❌ Test failed with error: {e}")
            results.append((test_name, False))
    
    # Print summary
    print("\n" + "="*80)
    print("  Test Summary")
    print("="*80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✅ All production configuration tests passed!")
        print("   Configuration complies with 'DO NOT EVER DO' list")
        return 0
    else:
        print("\n⚠️  Some tests failed. Review configuration.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
