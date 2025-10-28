import sqlite3
from pathlib import Path


def add_video_url_to_stories():
    """Add video_url column to existing stories table"""

    # Database path
    db_path = Path(__file__).parent / "hirebahamas.db"

    if not db_path.exists():
        print(f"Database not found at {db_path}")
        return False

    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()

        # Check if video_url column already exists
        cursor.execute("PRAGMA table_info(stories)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]

        if "video_url" not in column_names:
            # Add video_url column
            cursor.execute(
                """
                ALTER TABLE stories ADD COLUMN video_url TEXT DEFAULT ''
            """
            )
            print("Added video_url column to stories table")
        else:
            print("video_url column already exists")

        conn.commit()
        conn.close()

        print("Stories table updated successfully!")
        return True

    except Exception as e:
        print(f"Error updating stories table: {str(e)}")
        return False


if __name__ == "__main__":
    add_video_url_to_stories()
