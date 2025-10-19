"""
Migration script to add username, occupation, and company_name
fields to users table
"""
import sqlite3


def migrate():
    db_path = 'hirebahamas.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(users)")
        columns = [row[1] for row in cursor.fetchall()]
        
        # Add username column if it doesn't exist
        if 'username' not in columns:
            print("Adding username column...")
            cursor.execute(
                "ALTER TABLE users ADD COLUMN username VARCHAR(50)"
            )
            conn.commit()
            print("✓ Username column added")
        else:
            print("✓ Username column already exists")
        
        # Add occupation column if it doesn't exist
        if 'occupation' not in columns:
            print("Adding occupation column...")
            cursor.execute(
                "ALTER TABLE users ADD COLUMN occupation VARCHAR(200)"
            )
            conn.commit()
            print("✓ Occupation column added")
        else:
            print("✓ Occupation column already exists")
        
        # Add company_name column if it doesn't exist
        if 'company_name' not in columns:
            print("Adding company_name column...")
            cursor.execute(
                "ALTER TABLE users ADD COLUMN company_name VARCHAR(200)"
            )
            conn.commit()
            print("✓ Company_name column added")
        else:
            print("✓ Company_name column already exists")
        
        print("\n✅ Migration completed successfully!")
        
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        import traceback
        traceback.print_exc()
        conn.rollback()
    finally:
        conn.close()


if __name__ == "__main__":
    migrate()
