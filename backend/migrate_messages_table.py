"""
Migration script to add receiver_id and is_read columns to messages table
"""
import asyncio
import logging
from sqlalchemy import text
from app.database import engine, init_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def migrate_messages_table():
    """Add missing columns to messages table"""
    logger.info("Starting messages table migration...")
    
    try:
        async with engine.begin() as conn:
            # Check if columns already exist
            result = await conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'messages'
            """))
            existing_columns = [row[0] for row in result]
            
            # Add receiver_id if it doesn't exist
            if 'receiver_id' not in existing_columns:
                logger.info("Adding receiver_id column to messages table...")
                await conn.execute(text("""
                    ALTER TABLE messages 
                    ADD COLUMN receiver_id INTEGER REFERENCES users(id)
                """))
                logger.info("receiver_id column added successfully")
            else:
                logger.info("receiver_id column already exists")
            
            # Add is_read if it doesn't exist
            if 'is_read' not in existing_columns:
                logger.info("Adding is_read column to messages table...")
                await conn.execute(text("""
                    ALTER TABLE messages 
                    ADD COLUMN is_read BOOLEAN DEFAULT FALSE
                """))
                logger.info("is_read column added successfully")
            else:
                logger.info("is_read column already exists")
            
            # Update existing messages to set receiver_id based on conversation participants
            logger.info("Updating existing messages with receiver_id...")
            await conn.execute(text("""
                UPDATE messages m
                SET receiver_id = (
                    SELECT CASE 
                        WHEN c.participant_1_id = m.sender_id THEN c.participant_2_id
                        ELSE c.participant_1_id
                    END
                    FROM conversations c
                    WHERE c.id = m.conversation_id
                )
                WHERE receiver_id IS NULL
            """))
            logger.info("Existing messages updated successfully")
            
        logger.info("Migration completed successfully!")
        
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        raise


async def main():
    """Main migration function"""
    try:
        # Initialize database if needed
        await init_db()
        
        # Run migration
        await migrate_messages_table()
        
    except Exception as e:
        logger.error(f"Error during migration: {e}")
        raise
    finally:
        # Close database connections
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
