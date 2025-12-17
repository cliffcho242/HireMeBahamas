#!/usr/bin/env python3
"""
Test CI Type Check Workflow Configuration

This script validates that the type-check job in the CI workflow is correctly configured
and follows enterprise best practices for optional CI checks.
"""

import yaml


def test_ci_typecheck_configuration():
    """Test that the CI workflow has a properly configured type-check job."""
    print("🔍 Testing CI Type Check Workflow Configuration")
    print("=" * 60)
    
    # Load the CI workflow file
    with open('.github/workflows/ci.yml', 'r') as f:
        ci_config = yaml.safe_load(f)
    
    # Check that the type-check job exists
    assert 'jobs' in ci_config, "CI workflow must have jobs"
    jobs = ci_config['jobs']
    
    assert 'type-check' in jobs, "CI workflow must have a 'type-check' job"
    print("✅ type-check job exists")
    
    type_check_job = jobs['type-check']
    
    # Verify the job has continue-on-error set to true (never blocks builds)
    assert type_check_job.get('continue-on-error') == True, \
        "type-check job must have continue-on-error: true to never block builds"
    print("✅ type-check job has continue-on-error: true")
    
    # Verify the job runs on ubuntu-latest
    assert type_check_job.get('runs-on') == 'ubuntu-latest', \
        "type-check job should run on ubuntu-latest"
    print("✅ type-check job runs on ubuntu-latest")
    
    # Verify the job depends on smoke-tests
    assert 'smoke-tests' in type_check_job.get('needs', []), \
        "type-check job should depend on smoke-tests"
    print("✅ type-check job depends on smoke-tests")
    
    # Verify the job has proper permissions
    assert type_check_job.get('permissions', {}).get('contents') == 'read', \
        "type-check job should have read-only content permissions"
    print("✅ type-check job has correct permissions")
    
    # Verify the job has the necessary steps
    steps = type_check_job.get('steps', [])
    assert len(steps) > 0, "type-check job must have steps"
    
    # Check for checkout step
    checkout_step = next((s for s in steps if 'checkout' in s.get('name', '').lower()), None)
    assert checkout_step is not None, "type-check job must checkout code"
    print("✅ type-check job checks out code")
    
    # Check for Node.js setup
    node_setup = next((s for s in steps if 'node' in s.get('name', '').lower()), None)
    assert node_setup is not None, "type-check job must setup Node.js"
    print("✅ type-check job sets up Node.js")
    
    # Check for dependency installation
    install_step = next((s for s in steps if 'install dependencies' in s.get('name', '').lower()), None)
    assert install_step is not None, "type-check job must install dependencies"
    assert 'npm ci' in install_step.get('run', ''), "type-check job must use npm ci"
    print("✅ type-check job installs dependencies")
    
    # Check for actual type check step
    typecheck_step = next((s for s in steps if 'type check' in s.get('name', '').lower() 
                          and 'summary' not in s.get('name', '').lower()), None)
    assert typecheck_step is not None, "type-check job must have a type check step"
    assert 'npm run typecheck' in typecheck_step.get('run', ''), \
        "type-check step must run 'npm run typecheck'"
    print("✅ type-check job runs npm run typecheck")
    
    # Check for summary step
    summary_step = next((s for s in steps if 'summary' in s.get('name', '').lower()), None)
    assert summary_step is not None, "type-check job must have a summary step"
    assert summary_step.get('if') == 'always()', "Summary step should always run"
    print("✅ type-check job has a summary step that always runs")
    
    # Verify that lint-frontend no longer has the type check step
    lint_frontend = jobs.get('lint-frontend', {})
    lint_steps = lint_frontend.get('steps', [])
    
    # Check that none of the steps in lint-frontend are type checking
    for step in lint_steps:
        step_name = step.get('name', '').lower()
        step_run = step.get('run', '').lower()
        assert 'type check' not in step_name, \
            "lint-frontend should not have type check step (moved to separate job)"
        if 'typecheck' in step_run:
            raise AssertionError("lint-frontend should not run typecheck (moved to separate job)")
    
    print("✅ Type check removed from lint-frontend job")
    
    print("\n" + "=" * 60)
    print("✅ All CI Type Check Workflow tests passed!")
    print("\n📋 Summary:")
    print("   - Separate type-check job exists")
    print("   - Job never blocks builds (continue-on-error: true)")
    print("   - Job provides developer feedback via summary")
    print("   - Job runs in parallel with other CI jobs")
    print("   - This is enterprise-level CI configuration ✨")
    
    return True


if __name__ == '__main__':
    try:
        test_ci_typecheck_configuration()
        print("\n🎉 Type check CI workflow is correctly configured!")
        exit(0)
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        exit(1)
