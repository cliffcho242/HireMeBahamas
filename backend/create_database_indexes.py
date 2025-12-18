"""
Database Indexes Migration for Performance Optimization

This migration adds optimized indexes to improve query performance
following Meta's TAO/MySQL sharding patterns adapted for PostgreSQL.

Performance targets:
- Login queries: <5ms (email index)
- Posts feed: <10ms (user_id + created_at composite)
- Messages: <10ms (receiver_id + is_read)
- Jobs search: <15ms (category, location, is_remote combined)

Run this script on your PostgreSQL database:
    python backend/create_database_indexes.py

For Railway/Render, add to your build command:
    python backend/create_database_indexes.py
"""
import asyncio
import logging
import sys
import os
from urllib.parse import urlparse, urlunparse, parse_qs, urlencode

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from decouple import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Index definitions with descriptions
# Format: (table, index_name, columns, is_unique, where_clause)
INDEXES = [
    # =========================================================================
    # USER INDEXES - Critical for authentication and profile lookups
    # =========================================================================
    (
        "users",
        "idx_users_email_lower",
        "lower(email)",
        True,
        None,
        "Case-insensitive email lookup for login"
    ),
    (
        "users",
        "idx_users_phone",
        "phone",
        False,
        "phone IS NOT NULL",
        "Phone number login support"
    ),
    (
        "users",
        "idx_users_active_role",
        "role, is_active",
        False,
        "is_active = true",
        "Filter active users by role"
    ),
    (
        "users",
        "idx_users_available_for_hire",
        "is_available_for_hire, is_active",
        False,
        "is_available_for_hire = true AND is_active = true",
        "HireMe page query optimization"
    ),
    (
        "users",
        "idx_users_oauth",
        "oauth_provider, oauth_provider_id",
        False,
        "oauth_provider IS NOT NULL",
        "OAuth login lookup"
    ),
    
    # =========================================================================
    # JOBS INDEXES - Search and filtering optimization
    # =========================================================================
    (
        "jobs",
        "idx_jobs_employer_created",
        "employer_id, created_at DESC",
        False,
        None,
        "User's posted jobs listing"
    ),
    (
        "jobs",
        "idx_jobs_category_status",
        "category, status",
        False,
        "status = 'active'",
        "Category filtering for active jobs"
    ),
    (
        "jobs",
        "idx_jobs_location_remote",
        "location, is_remote",
        False,
        "status = 'active'",
        "Location and remote job filtering"
    ),
    (
        "jobs",
        "idx_jobs_salary_range",
        "salary_min, salary_max",
        False,
        "salary_min IS NOT NULL AND salary_max IS NOT NULL",
        "Salary range filtering"
    ),
    (
        "jobs",
        "idx_jobs_active_created",
        "created_at DESC",
        False,
        "status = 'active'",
        "Latest active jobs listing"
    ),
    (
        "jobs",
        "idx_jobs_title_trgm",
        "title gin_trgm_ops",
        False,
        None,
        "Full-text search on job titles (requires pg_trgm extension)"
    ),
    
    # =========================================================================
    # POSTS INDEXES - Social feed optimization (Meta-style)
    # =========================================================================
    (
        "posts",
        "idx_posts_user_created",
        "user_id, created_at DESC",
        False,
        None,
        "User's posts listing (profile page)"
    ),
    (
        "posts",
        "idx_posts_feed",
        "created_at DESC",
        False,
        None,
        "Global feed chronological ordering"
    ),
    (
        "posts",
        "idx_posts_type_created",
        "post_type, created_at DESC",
        False,
        None,
        "Filter posts by type"
    ),
    
    # =========================================================================
    # POST LIKES INDEXES - Like/unlike optimization
    # =========================================================================
    (
        "post_likes",
        "idx_post_likes_post_user",
        "post_id, user_id",
        True,
        None,
        "Unique constraint: one like per user per post"
    ),
    (
        "post_likes",
        "idx_post_likes_user",
        "user_id",
        False,
        None,
        "User's liked posts lookup"
    ),
    
    # =========================================================================
    # POST COMMENTS INDEXES - Comment retrieval
    # =========================================================================
    (
        "post_comments",
        "idx_post_comments_post_created",
        "post_id, created_at ASC",
        False,
        None,
        "Comments for a post in chronological order"
    ),
    (
        "post_comments",
        "idx_post_comments_user",
        "user_id",
        False,
        None,
        "User's comments lookup"
    ),
    
    # =========================================================================
    # MESSAGES INDEXES - Real-time messaging optimization
    # =========================================================================
    (
        "messages",
        "idx_messages_conversation_created",
        "conversation_id, created_at DESC",
        False,
        None,
        "Messages in a conversation"
    ),
    (
        "messages",
        "idx_messages_receiver_unread",
        "receiver_id, is_read",
        False,
        "is_read = false",
        "Unread messages count"
    ),
    (
        "messages",
        "idx_messages_sender",
        "sender_id, created_at DESC",
        False,
        None,
        "Sent messages lookup"
    ),
    
    # =========================================================================
    # CONVERSATIONS INDEXES - Messaging participant lookup
    # =========================================================================
    (
        "conversations",
        "idx_conversations_participant1",
        "participant_1_id, updated_at DESC",
        False,
        None,
        "User's conversations (as participant 1)"
    ),
    (
        "conversations",
        "idx_conversations_participant2",
        "participant_2_id, updated_at DESC",
        False,
        None,
        "User's conversations (as participant 2)"
    ),
    (
        "conversations",
        "idx_conversations_participants",
        "participant_1_id, participant_2_id",
        True,
        None,
        "Unique conversation between two users"
    ),
    
    # =========================================================================
    # NOTIFICATIONS INDEXES - Real-time notification delivery
    # =========================================================================
    (
        "notifications",
        "idx_notifications_user_unread",
        "user_id, is_read, created_at DESC",
        False,
        None,
        "User's unread notifications count"
    ),
    (
        "notifications",
        "idx_notifications_user_created",
        "user_id, created_at DESC",
        False,
        None,
        "User's all notifications"
    ),
    (
        "notifications",
        "idx_notifications_type",
        "notification_type, created_at DESC",
        False,
        None,
        "Filter by notification type"
    ),
    
    # =========================================================================
    # FOLLOWS INDEXES - Social graph optimization
    # =========================================================================
    (
        "follows",
        "idx_follows_follower_followed",
        "follower_id, followed_id",
        True,
        None,
        "Unique follow relationship"
    ),
    (
        "follows",
        "idx_follows_followed",
        "followed_id",
        False,
        None,
        "User's followers list"
    ),
    (
        "follows",
        "idx_follows_follower",
        "follower_id",
        False,
        None,
        "User's following list"
    ),
    
    # =========================================================================
    # JOB APPLICATIONS INDEXES - Application tracking
    # =========================================================================
    (
        "job_applications",
        "idx_applications_job_status",
        "job_id, status",
        False,
        None,
        "Applications for a job by status"
    ),
    (
        "job_applications",
        "idx_applications_applicant",
        "applicant_id, created_at DESC",
        False,
        None,
        "User's job applications"
    ),
    (
        "job_applications",
        "idx_applications_job_applicant",
        "job_id, applicant_id",
        True,
        None,
        "Unique application per user per job"
    ),
    
    # =========================================================================
    # REVIEWS INDEXES - Rating/review lookup
    # =========================================================================
    (
        "reviews",
        "idx_reviews_reviewee",
        "reviewee_id, created_at DESC",
        False,
        None,
        "User's received reviews"
    ),
    (
        "reviews",
        "idx_reviews_reviewer",
        "reviewer_id",
        False,
        None,
        "User's given reviews"
    ),
    (
        "reviews",
        "idx_reviews_job",
        "job_id",
        False,
        None,
        "Reviews for a job"
    ),
    
    # =========================================================================
    # PROFILE PICTURES INDEXES - Profile image management
    # =========================================================================
    (
        "profile_pictures",
        "idx_profile_pictures_user_current",
        "user_id, is_current",
        False,
        "is_current = true",
        "Current profile picture lookup"
    ),
    (
        "profile_pictures",
        "idx_profile_pictures_user",
        "user_id, created_at DESC",
        False,
        None,
        "User's profile pictures history"
    ),
]


async def create_indexes():
    """Create all performance indexes."""
    import asyncpg
    
    DATABASE_URL = config(
        "DATABASE_PRIVATE_URL",
        default=config(
            "DATABASE_URL", 
            default="postgresql://hiremebahamas_user:hiremebahamas_password@localhost:5432/hiremebahamas"
        )
    )
    
    # Convert async URL to sync
    if DATABASE_URL.startswith("postgresql+asyncpg://"):
        DATABASE_URL = DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://", 1)
    
    # Strip sslmode parameter - asyncpg handles SSL automatically
    parsed = urlparse(DATABASE_URL)
    if parsed.query and 'sslmode' in parsed.query:
        query_params = parse_qs(parsed.query)
        if 'sslmode' in query_params:
            del query_params['sslmode']
        new_query = urlencode(query_params, doseq=True)
        DATABASE_URL = urlunparse((
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            parsed.params,
            new_query,
            parsed.fragment
        ))
    
    logger.info(f"Connecting to database...")
    
    try:
        conn = await asyncpg.connect(DATABASE_URL)
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        return False
    
    try:
        # Enable pg_trgm extension for full-text search indexes
        logger.info("Enabling pg_trgm extension...")
        try:
            await conn.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm;")
            logger.info("pg_trgm extension enabled")
        except Exception as e:
            logger.warning(f"Could not enable pg_trgm (may require superuser): {e}")
        
        created_count = 0
        skipped_count = 0
        failed_count = 0
        
        for index_def in INDEXES:
            table, index_name, columns, is_unique, where_clause, description = index_def
            
            # Check if index already exists
            exists = await conn.fetchval("""
                SELECT EXISTS (
                    SELECT 1 FROM pg_indexes 
                    WHERE indexname = $1
                )
            """, index_name)
            
            if exists:
                logger.info(f"  SKIP: {index_name} (already exists)")
                skipped_count += 1
                continue
            
            # Build CREATE INDEX statement
            unique_clause = "UNIQUE" if is_unique else ""
            where_sql = f"WHERE {where_clause}" if where_clause else ""
            
            # Handle GIN indexes for full-text search
            if "gin_trgm_ops" in columns:
                col_name = columns.replace(" gin_trgm_ops", "")
                sql = f"""
                    CREATE INDEX CONCURRENTLY IF NOT EXISTS {index_name} 
                    ON {table} USING gin ({col_name} gin_trgm_ops)
                    {where_sql}
                """
            else:
                sql = f"""
                    CREATE {unique_clause} INDEX CONCURRENTLY IF NOT EXISTS {index_name} 
                    ON {table} ({columns})
                    {where_sql}
                """
            
            try:
                logger.info(f"  CREATE: {index_name} - {description}")
                await conn.execute(sql)
                created_count += 1
            except Exception as e:
                logger.error(f"  FAILED: {index_name} - {e}")
                failed_count += 1
        
        logger.info(f"\nIndex creation complete:")
        logger.info(f"  Created: {created_count}")
        logger.info(f"  Skipped: {skipped_count}")
        logger.info(f"  Failed: {failed_count}")
        
        return failed_count == 0
        
    finally:
        await conn.close()


async def analyze_tables():
    """Run ANALYZE on tables to update statistics after creating indexes."""
    import asyncpg
    
    DATABASE_URL = config(
        "DATABASE_PRIVATE_URL",
        default=config(
            "DATABASE_URL", 
            default="postgresql://hiremebahamas_user:hiremebahamas_password@localhost:5432/hiremebahamas"
        )
    )
    
    if DATABASE_URL.startswith("postgresql+asyncpg://"):
        DATABASE_URL = DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://", 1)
    
    # Strip sslmode parameter - asyncpg handles SSL automatically
    parsed = urlparse(DATABASE_URL)
    if parsed.query and 'sslmode' in parsed.query:
        query_params = parse_qs(parsed.query)
        if 'sslmode' in query_params:
            del query_params['sslmode']
        new_query = urlencode(query_params, doseq=True)
        DATABASE_URL = urlunparse((
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            parsed.params,
            new_query,
            parsed.fragment
        ))
    
    tables = list(set(idx[0] for idx in INDEXES))
    
    logger.info(f"Running ANALYZE on {len(tables)} tables...")
    
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        for table in tables:
            try:
                await conn.execute(f"ANALYZE {table};")
                logger.info(f"  ANALYZED: {table}")
            except Exception as e:
                logger.warning(f"  FAILED to analyze {table}: {e}")
        await conn.close()
    except Exception as e:
        logger.error(f"Failed to run ANALYZE: {e}")


async def main():
    """Main entry point."""
    logger.info("=" * 60)
    logger.info("HireMeBahamas Database Index Migration")
    logger.info("Meta-inspired performance optimization")
    logger.info("=" * 60)
    
    success = await create_indexes()
    
    if success:
        await analyze_tables()
        logger.info("\n✅ Migration completed successfully!")
    else:
        logger.error("\n❌ Migration completed with errors")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
