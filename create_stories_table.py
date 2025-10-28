import sqlite3
from pathlib import Path


def create_stories_table():
    """Create stories table in the existing database"""

    # Database path
    db_path = Path(__file__).parent / "hirebahamas.db"

    if not db_path.exists():
        print(f"Database not found at {db_path}")
        return False

    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()

        # Create stories table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS stories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                content TEXT NOT NULL,
                image_path TEXT DEFAULT '',
                video_path TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
        """
        )

        conn.commit()
        conn.close()

        print("Stories table created successfully!")
        return True

    except Exception as e:
        print(f"Error creating stories table: {str(e)}")
        return False


if __name__ == "__main__":
    create_stories_table()
