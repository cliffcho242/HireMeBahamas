"""
Migration script for SQLite to add receiver_id and is_read columns to messages table
"""
import sqlite3
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "hiremebahamas.db")


def migrate_sqlite_messages_table():
    """Add missing columns to messages table for SQLite"""
    logger.info("Starting SQLite messages table migration...")
    logger.info(f"Database path: {DB_PATH}")
    
    if not os.path.exists(DB_PATH):
        logger.warning("Database file does not exist. It will be created on first run.")
        return
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(messages)")
        existing_columns = [row[1] for row in cursor.fetchall()]
        
        # Add receiver_id if it doesn't exist
        if 'receiver_id' not in existing_columns:
            logger.info("Adding receiver_id column to messages table...")
            cursor.execute("""
                ALTER TABLE messages 
                ADD COLUMN receiver_id INTEGER REFERENCES users(id)
            """)
            logger.info("receiver_id column added successfully")
        else:
            logger.info("receiver_id column already exists")
        
        # Add is_read if it doesn't exist
        if 'is_read' not in existing_columns:
            logger.info("Adding is_read column to messages table...")
            cursor.execute("""
                ALTER TABLE messages 
                ADD COLUMN is_read BOOLEAN DEFAULT 0
            """)
            logger.info("is_read column added successfully")
        else:
            logger.info("is_read column already exists")
        
        # Update existing messages to set receiver_id based on conversation participants
        # Only update if receiver_id was just added or if there are NULL values
        logger.info("Checking for messages with NULL receiver_id...")
        cursor.execute("SELECT COUNT(*) FROM messages WHERE receiver_id IS NULL")
        null_count = cursor.fetchone()[0]
        
        if null_count > 0:
            logger.info(f"Updating {null_count} existing messages with receiver_id...")
            cursor.execute("""
                UPDATE messages 
                SET receiver_id = (
                    SELECT CASE 
                        WHEN c.participant_1_id = m.sender_id THEN c.participant_2_id
                        ELSE c.participant_1_id
                    END
                    FROM conversations c
                    WHERE c.id = m.conversation_id
                )
                FROM messages m
                WHERE messages.id = m.id AND messages.receiver_id IS NULL
            """)
            logger.info("Existing messages updated successfully")
        else:
            logger.info("All messages already have receiver_id set")
        
        conn.commit()
        conn.close()
        
        logger.info("SQLite migration completed successfully!")
        
    except sqlite3.Error as e:
        logger.error(f"SQLite migration failed: {e}")
        raise


if __name__ == "__main__":
    migrate_sqlite_messages_table()
