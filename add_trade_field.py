#!/usr/bin/env python3
"""
Add trade/skill field to users table for HireMe search functionality
"""

import sqlite3
import os

def add_trade_field():
    """Add trade field to users table"""
    db_path = os.path.join(os.path.dirname(__file__), 'hirebahamas.db')

    if not os.path.exists(db_path):
        print("Database not found!")
        return False

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Check if trade column already exists
        cursor.execute("PRAGMA table_info(users)")
        columns = [col[1] for col in cursor.fetchall()]

        if 'trade' not in columns:
            print("Adding trade column to users table...")
            cursor.execute("ALTER TABLE users ADD COLUMN trade TEXT DEFAULT ''")
            conn.commit()
            print("✅ Trade column added successfully!")
        else:
            print("✅ Trade column already exists")

        # Add some sample trades to existing users
        print("Adding sample trades to users...")
        sample_trades = [
            ('Plumber', 'admin@hirebahamas.com'),
            ('Electrician', 'testuser@example.com'),
            ('Software Developer', 'admin@hirebahamas.com'),
            ('Graphic Designer', 'testuser@example.com'),
            ('Carpenter', 'admin@hirebahamas.com'),
            ('Chef', 'testuser@example.com')
        ]

        for trade, email in sample_trades:
            cursor.execute("UPDATE users SET trade = ? WHERE email = ?", (trade, email))

        conn.commit()
        print("✅ Sample trades added to users")

        conn.close()
        return True

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    print("🔧 Adding trade field to HireBahamas database...")
    success = add_trade_field()
    if success:
        print("🎉 Database migration completed successfully!")
    else:
        print("❌ Database migration failed!")