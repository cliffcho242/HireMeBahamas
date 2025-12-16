"""
Database Index Migration - Step 10: Scaling to 100K+ Users
============================================================
Adds indexes to heavily accessed columns for better query performance.

This migration script adds database indexes to improve query performance
at scale. These indexes are essential for handling 100K+ concurrent users.

Usage:
    python migrations/add_performance_indexes.py

Note: This script is idempotent - it checks if indexes exist before creating them.
"""
import os
import sys
import asyncio
import logging
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Index definitions
# Format: (table_name, index_name, columns, is_unique)
INDEXES = [
    # Job table indexes
    ("jobs", "idx_jobs_employer_id", ["employer_id"], False),
    ("jobs", "idx_jobs_status", ["status"], False),
    ("jobs", "idx_jobs_category", ["category"], False),
    ("jobs", "idx_jobs_location", ["location"], False),
    ("jobs", "idx_jobs_created_at", ["created_at"], False),
    ("jobs", "idx_jobs_status_created", ["status", "created_at"], False),  # Composite for active jobs sorted by date
    
    # Job application indexes
    ("job_applications", "idx_job_applications_job_id", ["job_id"], False),
    ("job_applications", "idx_job_applications_applicant_id", ["applicant_id"], False),
    ("job_applications", "idx_job_applications_status", ["status"], False),
    ("job_applications", "idx_job_applications_created_at", ["created_at"], False),
    
    # Message indexes
    ("messages", "idx_messages_conversation_id", ["conversation_id"], False),
    ("messages", "idx_messages_sender_id", ["sender_id"], False),
    ("messages", "idx_messages_receiver_id", ["receiver_id"], False),
    ("messages", "idx_messages_is_read", ["is_read"], False),
    ("messages", "idx_messages_created_at", ["created_at"], False),
    ("messages", "idx_messages_receiver_unread", ["receiver_id", "is_read"], False),  # Composite for unread messages
    
    # Notification indexes
    ("notifications", "idx_notifications_user_id", ["user_id"], False),
    ("notifications", "idx_notifications_actor_id", ["actor_id"], False),
    ("notifications", "idx_notifications_type", ["notification_type"], False),
    ("notifications", "idx_notifications_is_read", ["is_read"], False),
    ("notifications", "idx_notifications_related_id", ["related_id"], False),
    ("notifications", "idx_notifications_created_at", ["created_at"], False),
    ("notifications", "idx_notifications_user_unread", ["user_id", "is_read"], False),  # Composite for unread notifications
    ("notifications", "idx_notifications_user_type", ["user_id", "notification_type"], False),  # Composite for filtering by type
    
    # Post indexes
    ("posts", "idx_posts_user_id", ["user_id"], False),
    ("posts", "idx_posts_type", ["post_type"], False),
    ("posts", "idx_posts_related_job_id", ["related_job_id"], False),
    ("posts", "idx_posts_created_at", ["created_at"], False),
    ("posts", "idx_posts_user_created", ["user_id", "created_at"], False),  # Composite for user's posts by date
    
    # Post like indexes
    ("post_likes", "idx_post_likes_post_id", ["post_id"], False),
    ("post_likes", "idx_post_likes_user_id", ["user_id"], False),
    ("post_likes", "idx_post_likes_created_at", ["created_at"], False),
    ("post_likes", "idx_post_likes_user_post", ["user_id", "post_id"], True),  # Unique composite - user can like post once
    
    # Post comment indexes
    ("post_comments", "idx_post_comments_post_id", ["post_id"], False),
    ("post_comments", "idx_post_comments_user_id", ["user_id"], False),
    ("post_comments", "idx_post_comments_created_at", ["created_at"], False),
    
    # Follow indexes
    ("follows", "idx_follows_follower_id", ["follower_id"], False),
    ("follows", "idx_follows_followed_id", ["followed_id"], False),
    ("follows", "idx_follows_created_at", ["created_at"], False),
    ("follows", "idx_follows_relationship", ["follower_id", "followed_id"], True),  # Unique composite
]


async def index_exists(session: AsyncSession, table_name: str, index_name: str) -> bool:
    """Check if an index already exists."""
    try:
        # PostgreSQL query to check if index exists
        query = text("""
            SELECT 1 FROM pg_indexes 
            WHERE indexname = :index_name 
            AND tablename = :table_name
        """)
        result = await session.execute(query, {"index_name": index_name, "table_name": table_name})
        return result.scalar() is not None
    except Exception as e:
        logger.warning(f"Error checking if index exists: {e}")
        return False


async def create_index(session: AsyncSession, table_name: str, index_name: str, columns: list, is_unique: bool = False):
    """Create an index if it doesn't already exist."""
    try:
        # Check if index exists
        exists = await index_exists(session, table_name, index_name)
        if exists:
            logger.info(f"Index {index_name} already exists on {table_name}, skipping...")
            return True
        
        # Build CREATE INDEX statement
        unique_clause = "UNIQUE" if is_unique else ""
        columns_str = ", ".join(columns)
        query = text(f"""
            CREATE {unique_clause} INDEX {index_name} 
            ON {table_name} ({columns_str})
        """)
        
        logger.info(f"Creating index {index_name} on {table_name}({columns_str})...")
        await session.execute(query)
        await session.commit()
        logger.info(f"✓ Successfully created index {index_name}")
        return True
        
    except Exception as e:
        logger.error(f"✗ Failed to create index {index_name}: {e}")
        await session.rollback()
        return False


async def run_migration():
    """Run the migration to add all indexes."""
    # Get database URL from environment
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        logger.error("DATABASE_URL environment variable not set")
        return False
    
    # Ensure asyncpg driver
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql+asyncpg://", 1)
    elif not database_url.startswith("postgresql+asyncpg://"):
        database_url = "postgresql+asyncpg://" + database_url.split("://", 1)[1]
    
    logger.info(f"Connecting to database...")
    
    # Create engine and session
    engine = create_async_engine(database_url, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    success_count = 0
    fail_count = 0
    skip_count = 0
    
    async with async_session() as session:
        logger.info(f"\nStarting index migration...")
        logger.info(f"Creating {len(INDEXES)} indexes...\n")
        
        for table_name, index_name, columns, is_unique in INDEXES:
            # Check if already exists first
            exists = await index_exists(session, table_name, index_name)
            if exists:
                skip_count += 1
                continue
            
            # Create the index
            success = await create_index(session, table_name, index_name, columns, is_unique)
            if success:
                success_count += 1
            else:
                fail_count += 1
    
    await engine.dispose()
    
    # Print summary
    logger.info(f"\n{'='*60}")
    logger.info(f"Migration Summary:")
    logger.info(f"  ✓ Successfully created: {success_count} indexes")
    logger.info(f"  ⊘ Already existed:      {skip_count} indexes")
    logger.info(f"  ✗ Failed:               {fail_count} indexes")
    logger.info(f"{'='*60}\n")
    
    return fail_count == 0


async def verify_indexes():
    """Verify that critical indexes exist."""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        logger.error("DATABASE_URL environment variable not set")
        return False
    
    # Ensure asyncpg driver
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql+asyncpg://", 1)
    elif not database_url.startswith("postgresql+asyncpg://"):
        database_url = "postgresql+asyncpg://" + database_url.split("://", 1)[1]
    
    engine = create_async_engine(database_url, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        logger.info("\nVerifying critical indexes...")
        
        critical_indexes = [
            ("jobs", "idx_jobs_status_created"),
            ("notifications", "idx_notifications_user_unread"),
            ("messages", "idx_messages_receiver_unread"),
            ("post_likes", "idx_post_likes_user_post"),
        ]
        
        all_exist = True
        for table_name, index_name in critical_indexes:
            exists = await index_exists(session, table_name, index_name)
            status = "✓" if exists else "✗"
            logger.info(f"  {status} {table_name}.{index_name}")
            if not exists:
                all_exist = False
    
    await engine.dispose()
    return all_exist


if __name__ == "__main__":
    logger.info("="*60)
    logger.info("Database Index Migration - Step 10: Scaling to 100K+ Users")
    logger.info("="*60)
    
    # Run migration
    success = asyncio.run(run_migration())
    
    if success:
        logger.info("\n✓ Migration completed successfully!")
        
        # Verify critical indexes
        asyncio.run(verify_indexes())
    else:
        logger.error("\n✗ Migration completed with errors")
        sys.exit(1)
