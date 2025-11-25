#!/usr/bin/env python3
"""
Test script to verify database admin interface configuration
"""

import sys
import yaml


def test_docker_compose():
    """Test docker-compose.yml configuration"""
    print("🔍 Testing docker-compose.yml configuration...")
    
    try:
        with open('docker-compose.yml', 'r') as f:
            config = yaml.safe_load(f)
        
        # Check if adminer service exists
        if 'adminer' not in config.get('services', {}):
            print("❌ Adminer service not found in docker-compose.yml")
            return False
        
        adminer = config['services']['adminer']
        
        # Check image
        if not adminer.get('image', '').startswith('adminer:'):
            print("❌ Adminer image is not set correctly")
            return False
        
        # Check ports
        ports = adminer.get('ports', [])
        if not any('8081:8080' in str(port) for port in ports):
            print("❌ Adminer port 8081:8080 not configured")
            return False
        
        # Check environment variables
        env = adminer.get('environment', {})
        if env.get('ADMINER_DEFAULT_SERVER') != 'postgres':
            print("❌ ADMINER_DEFAULT_SERVER should be 'postgres'")
            return False
        
        # Check depends_on
        depends_on = adminer.get('depends_on', {})
        if 'postgres' not in depends_on:
            print("❌ Adminer should depend on postgres service")
            return False
        
        print("✅ Docker Compose configuration is correct")
        print(f"   - Image: {adminer.get('image')}")
        print(f"   - Port: {ports[0] if ports else 'Not set'}")
        print(f"   - Default Server: {env.get('ADMINER_DEFAULT_SERVER')}")
        print(f"   - Design: {env.get('ADMINER_DESIGN', 'default')}")
        return True
        
    except FileNotFoundError:
        print("❌ docker-compose.yml not found")
        return False
    except yaml.YAMLError as e:
        print(f"❌ Invalid YAML in docker-compose.yml: {e}")
        return False
    except Exception as e:
        print(f"❌ Error testing docker-compose.yml: {e}")
        return False


def test_documentation():
    """Test if documentation files exist"""
    print("\n🔍 Testing documentation files...")
    
    docs = [
        'DATABASE_ADMIN_INTERFACE.md',
        'DATABASE_INTERFACE_QUICK_REF.md',
    ]
    
    all_exist = True
    for doc in docs:
        try:
            with open(doc, 'r') as f:
                content = f.read()
                if len(content) < 100:
                    print(f"⚠️  {doc} exists but seems too short")
                    all_exist = False
                else:
                    print(f"✅ {doc} exists and has content")
        except FileNotFoundError:
            print(f"❌ {doc} not found")
            all_exist = False
    
    return all_exist


def test_readme_reference():
    """Test if README mentions the database interface"""
    print("\n🔍 Testing README.md references...")
    
    try:
        with open('README.md', 'r') as f:
            content = f.read()
        
        keywords = [
            'database admin',
            'adminer',
            'DATABASE_ADMIN_INTERFACE',
        ]
        
        found = False
        for keyword in keywords:
            if keyword.lower() in content.lower():
                print(f"✅ Found reference to '{keyword}' in README.md")
                found = True
                break
        
        if not found:
            print("⚠️  No database admin interface references found in README.md")
            return False
        
        return True
        
    except FileNotFoundError:
        print("❌ README.md not found")
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("Database Admin Interface Configuration Test")
    print("=" * 60)
    
    tests = [
        test_docker_compose,
        test_documentation,
        test_readme_reference,
    ]
    
    results = [test() for test in tests]
    
    print("\n" + "=" * 60)
    if all(results):
        print("✅ All tests passed!")
        print("\nNext steps:")
        print("1. Run: docker-compose up -d postgres adminer")
        print("2. Open: http://localhost:8081")
        print("3. Login with credentials from docker-compose.yml:")
        print("   - Server: postgres")
        print("   - Username: hiremebahamas_user")
        print("   - Password: hiremebahamas_password")
        print("   - Database: hiremebahamas")
        print("\n⚠️  Note: These are development credentials only!")
        print("=" * 60)
        return 0
    else:
        print("❌ Some tests failed")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())
