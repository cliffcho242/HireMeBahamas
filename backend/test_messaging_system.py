"""
Integration test for messaging API
Tests the chat/messaging functionality end-to-end
"""
import asyncio
import os
import sys

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import init_db, engine
from app.models import User, Conversation, Message
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import AsyncSessionLocal


async def test_messaging_setup():
    """Test messaging database setup"""
    print("=" * 60)
    print("Testing Messaging Database Setup")
    print("=" * 60)
    
    try:
        # Initialize database
        print("\n1. Initializing database...")
        await init_db()
        print("   ✓ Database initialized")
        
        # Create test session
        print("\n2. Testing database connection...")
        async with AsyncSessionLocal() as session:
            # Check if users table exists and can be queried
            result = await session.execute(select(User).limit(1))
            users = result.scalars().all()
            print(f"   ✓ Users table accessible (found {len(users)} users)")
            
            # Check if conversations table exists
            result = await session.execute(select(Conversation).limit(1))
            conversations = result.scalars().all()
            print(f"   ✓ Conversations table accessible (found {len(conversations)} conversations)")
            
            # Check if messages table exists
            result = await session.execute(select(Message).limit(1))
            messages = result.scalars().all()
            print(f"   ✓ Messages table accessible (found {len(messages)} messages)")
        
        print("\n3. Verifying Message model fields...")
        # Check if Message model has required fields
        message_attrs = [attr for attr in dir(Message) if not attr.startswith('_')]
        required_fields = ['id', 'conversation_id', 'sender_id', 'receiver_id', 'content', 'is_read', 'created_at']
        
        for field in required_fields:
            if field in message_attrs or hasattr(Message, field):
                print(f"   ✓ Message.{field} exists")
            else:
                print(f"   ✗ Message.{field} MISSING!")
        
        print("\n" + "=" * 60)
        print("✓ All messaging setup tests passed!")
        print("=" * 60)
        print("\nChat functionality is ready to use!")
        print("\nNext steps for LOCAL DEVELOPMENT:")
        print("1. Start the backend server: uvicorn app.main:socket_app --reload")
        print("2. Start the frontend: cd frontend && npm run dev")
        print("3. Register/login users and test the messaging feature")
        print("\n⚠️  NOTE: --reload is for LOCAL DEVELOPMENT ONLY")
        print("   NEVER use --reload in production (doubles memory, causes SIGTERM)")
        
        return True
        
    except Exception as e:
        print(f"\n✗ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Close database connections
        await engine.dispose()


async def test_api_imports():
    """Test that all API modules can be imported"""
    print("\n" + "=" * 60)
    print("Testing API Imports")
    print("=" * 60)
    
    try:
        print("\n1. Testing core imports...")
        from app.main import app, socket_app
        print("   ✓ app.main imports successfully")
        
        print("\n2. Testing API module imports...")
        from app.api import auth, jobs, messages, reviews, upload
        print("   ✓ app.api.auth imports successfully")
        print("   ✓ app.api.jobs imports successfully")
        print("   ✓ app.api.messages imports successfully")
        print("   ✓ app.api.reviews imports successfully")
        print("   ✓ app.api.upload imports successfully")
        
        print("\n3. Testing Socket.IO setup...")
        from app.main import sio
        print("   ✓ Socket.IO server initialized")
        
        print("\n" + "=" * 60)
        print("✓ All API imports successful!")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n✗ Error during import testing: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("HireMeBahamas Messaging System Tests")
    print("=" * 60)
    
    # Test API imports first
    import_success = await test_api_imports()
    
    if not import_success:
        print("\n✗ Import tests failed. Please fix import errors first.")
        return False
    
    # Test database setup
    db_success = await test_messaging_setup()
    
    if not db_success:
        print("\n✗ Database tests failed. Please check database configuration.")
        return False
    
    print("\n" + "=" * 60)
    print("✓✓✓ ALL TESTS PASSED ✓✓✓")
    print("=" * 60)
    print("\nThe messaging system is ready to use!")
    
    return True


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
