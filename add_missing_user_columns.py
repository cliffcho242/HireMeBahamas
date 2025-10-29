"""
Add missing user profile columns to the database
Adds: username, occupation, company_name
"""

import sqlite3
import sys

def add_missing_columns():
    """Add missing user profile columns"""
    try:
        conn = sqlite3.connect('hiremebahamas.db')
        cursor = conn.cursor()
        
        print("🔧 Adding missing user profile columns...")
        
        # Check existing columns
        cursor.execute('PRAGMA table_info(users)')
        existing_columns = {col[1] for col in cursor.fetchall()}
        print(f"📋 Existing columns: {', '.join(existing_columns)}")
        
        # Add username column if it doesn't exist
        if 'username' not in existing_columns:
            print("  ➕ Adding 'username' column...")
            cursor.execute('''
                ALTER TABLE users ADD COLUMN username TEXT
            ''')
            print("  ✅ Added 'username' column")
        else:
            print("  ✓ 'username' column already exists")
        
        # Add occupation column if it doesn't exist
        if 'occupation' not in existing_columns:
            print("  ➕ Adding 'occupation' column...")
            cursor.execute('''
                ALTER TABLE users ADD COLUMN occupation TEXT
            ''')
            print("  ✅ Added 'occupation' column")
        else:
            print("  ✓ 'occupation' column already exists")
        
        # Add company_name column if it doesn't exist
        if 'company_name' not in existing_columns:
            print("  ➕ Adding 'company_name' column...")
            cursor.execute('''
                ALTER TABLE users ADD COLUMN company_name TEXT
            ''')
            print("  ✅ Added 'company_name' column")
        else:
            print("  ✓ 'company_name' column already exists")
        
        conn.commit()
        
        # Verify the changes
        cursor.execute('PRAGMA table_info(users)')
        updated_columns = [col[1] for col in cursor.fetchall()]
        print(f"\n✅ Migration complete! Current columns:")
        for col in updated_columns:
            print(f"   - {col}")
        
        # Check how many users we have
        cursor.execute('SELECT COUNT(*) FROM users')
        user_count = cursor.fetchone()[0]
        print(f"\n📊 Total users in database: {user_count}")
        
        # Show sample users
        if user_count > 0:
            cursor.execute('SELECT id, email, first_name, last_name FROM users LIMIT 5')
            users = cursor.fetchall()
            print("\n👤 Sample users:")
            for user in users:
                print(f"   ID: {user[0]}, Email: {user[1]}, Name: {user[2]} {user[3]}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🔧 USER PROFILE COLUMNS MIGRATION")
    print("=" * 60)
    
    success = add_missing_columns()
    
    if success:
        print("\n" + "=" * 60)
        print("✅ Migration completed successfully!")
        print("=" * 60)
        sys.exit(0)
    else:
        print("\n" + "=" * 60)
        print("❌ Migration failed!")
        print("=" * 60)
        sys.exit(1)
