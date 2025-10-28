#!/usr/bin/env python3
"""
Direct table creation script
"""

import sqlite3
from pathlib import Path


def create_tables_direct():
    """Create tables directly with SQLite"""

    db_path = Path(__file__).parent / "hirebahamas.db"

    # Remove existing database
    if db_path.exists():
        db_path.unlink()

    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    # Create users table with admin fields
    cursor.execute(
        """
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email VARCHAR(255) NOT NULL UNIQUE,
            hashed_password VARCHAR(255) NOT NULL,
            first_name VARCHAR(100) NOT NULL,
            last_name VARCHAR(100) NOT NULL,
            phone VARCHAR(20),
            location VARCHAR(200),
            bio TEXT,
            skills TEXT,
            experience TEXT,
            education TEXT,
            avatar_url VARCHAR(500),
            is_active BOOLEAN DEFAULT 1,
            is_admin BOOLEAN DEFAULT 0,
            role VARCHAR(50) DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
    )

    # Create other essential tables
    cursor.execute(
        """
        CREATE TABLE jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title VARCHAR(200) NOT NULL,
            description TEXT,
            requirements TEXT,
            location VARCHAR(200),
            job_type VARCHAR(50),
            salary_min DECIMAL(10,2),
            salary_max DECIMAL(10,2),
            is_active BOOLEAN DEFAULT 1,
            employer_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (employer_id) REFERENCES users (id)
        )
    """
    )

    conn.commit()
    conn.close()

    print("✅ Tables created successfully with admin support!")
    return True


if __name__ == "__main__":
    create_tables_direct()
