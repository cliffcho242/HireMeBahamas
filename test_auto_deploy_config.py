#!/usr/bin/env python3
"""
Test script to verify GitHub Actions workflows are properly configured
"""

import os
import sys
import yaml
from pathlib import Path

def test_workflow_files_exist():
    """Test that all required workflow files exist"""
    workflows_dir = Path('.github/workflows')
    required_workflows = [
        'ci.yml',
        'deploy-frontend.yml',
        'deploy-backend.yml',
        'deploy-backend-render.yml'
    ]
    
    print("Testing workflow files existence...")
    for workflow in required_workflows:
        workflow_path = workflows_dir / workflow
        if workflow_path.exists():
            print(f"  ✓ {workflow} exists")
        else:
            print(f"  ✗ {workflow} missing")
            return False
    return True

def test_workflow_yaml_valid():
    """Test that all workflow files are valid YAML"""
    workflows_dir = Path('.github/workflows')
    
    print("\nTesting YAML syntax...")
    for workflow_file in workflows_dir.glob('*.yml'):
        try:
            with open(workflow_file, 'r') as f:
                yaml.safe_load(f)
            print(f"  ✓ {workflow_file.name} is valid YAML")
        except yaml.YAMLError as e:
            print(f"  ✗ {workflow_file.name} has YAML error: {e}")
            return False
    return True

def test_workflow_structure():
    """Test that workflows have required fields"""
    workflows_dir = Path('.github/workflows')
    
    print("\nTesting workflow structure...")
    for workflow_file in workflows_dir.glob('*.yml'):
        with open(workflow_file, 'r') as f:
            workflow = yaml.safe_load(f)
        
        # Check for required top-level keys
        if 'name' not in workflow:
            print(f"  ✗ {workflow_file.name} missing 'name' field")
            return False
        
        if 'on' not in workflow:
            print(f"  ✗ {workflow_file.name} missing 'on' field")
            return False
        
        if 'jobs' not in workflow:
            print(f"  ✗ {workflow_file.name} missing 'jobs' field")
            return False
        
        print(f"  ✓ {workflow_file.name} has valid structure")
    
    return True

def test_documentation_exists():
    """Test that documentation files exist"""
    print("\nTesting documentation files...")
    docs = [
        'AUTO_DEPLOY_SETUP.md',
        'AUTO_DEPLOY_QUICK_REF.md'
    ]
    
    for doc in docs:
        if Path(doc).exists():
            print(f"  ✓ {doc} exists")
        else:
            print(f"  ✗ {doc} missing")
            return False
    return True

def test_readme_updated():
    """Test that README mentions auto-deploy"""
    print("\nTesting README.md updates...")
    with open('README.md', 'r') as f:
        content = f.read()
    
    if 'Auto-Deploy' in content or 'auto-deploy' in content.lower():
        print("  ✓ README.md mentions auto-deploy")
        return True
    else:
        print("  ✗ README.md doesn't mention auto-deploy")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("GitHub Actions Auto-Deploy Configuration Test")
    print("=" * 60)
    
    # Change to repository root
    repo_root = Path(__file__).parent
    os.chdir(repo_root)
    
    tests = [
        test_workflow_files_exist,
        test_workflow_yaml_valid,
        test_workflow_structure,
        test_documentation_exists,
        test_readme_updated
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"\n  ✗ Test failed with exception: {e}")
            results.append(False)
    
    print("\n" + "=" * 60)
    if all(results):
        print("✅ All tests passed! Auto-deploy is properly configured.")
        print("=" * 60)
        return 0
    else:
        print("❌ Some tests failed. Please review the output above.")
        print("=" * 60)
        return 1

if __name__ == '__main__':
    sys.exit(main())
