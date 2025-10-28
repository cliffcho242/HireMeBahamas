import sqlite3
from pathlib import Path


def migrate_stories_table():
    """Migrate stories table to use file paths instead of URLs"""

    # Database path
    db_path = Path(__file__).parent / "hirebahamas.db"

    if not db_path.exists():
        print(f"Database not found at {db_path}")
        return False

    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()

        # Check if columns already exist
        cursor.execute("PRAGMA table_info(stories)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]

        # Rename old columns if they exist
        if "image_url" in column_names and "image_path" not in column_names:
            cursor.execute("ALTER TABLE stories ADD COLUMN image_path TEXT DEFAULT ''")
            print("Added image_path column")

        if "video_url" in column_names and "video_path" not in column_names:
            cursor.execute("ALTER TABLE stories ADD COLUMN video_path TEXT DEFAULT ''")
            print("Added video_path column")

        # Copy data from old columns to new ones if they exist
        if "image_url" in column_names:
            cursor.execute(
                "UPDATE stories SET image_path = image_url WHERE image_url != ''"
            )
            print("Migrated image_url data to image_path")

        if "video_url" in column_names:
            cursor.execute(
                "UPDATE stories SET video_path = video_url WHERE video_url != ''"
            )
            print("Migrated video_url data to video_path")

        conn.commit()
        conn.close()

        print("Stories table migration completed successfully!")
        return True

    except Exception as e:
        print(f"Error migrating stories table: {str(e)}")
        return False


if __name__ == "__main__":
    migrate_stories_table()
