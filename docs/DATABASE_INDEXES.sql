-- =============================================================================
-- DATABASE INDEX RECOMMENDATIONS - VERCEL POSTGRES OPTIMIZED
-- =============================================================================
--
-- MASTERMIND VERCEL POSTGRES OPTIMIZATION (2025)
--
-- Index strategy for:
-- - < 1ms average query time
-- - 10k+ concurrent users support
-- - Optimized for Vercel Postgres + pgbouncer
--
-- Run this script after initial table creation.
--
-- =============================================================================

-- =============================================================================
-- USERS TABLE INDEXES
-- =============================================================================

-- Primary lookup indexes (BTREE - O(log n) lookups)
CREATE INDEX IF NOT EXISTS users_email_idx ON users (email);
CREATE INDEX IF NOT EXISTS users_username_idx ON users (username);
CREATE INDEX IF NOT EXISTS users_is_active_idx ON users (is_active) WHERE is_active = true;
CREATE INDEX IF NOT EXISTS users_is_available_for_hire_idx ON users (is_available_for_hire) WHERE is_available_for_hire = true;

-- OAuth lookup (for Google/Apple sign-in)
CREATE INDEX IF NOT EXISTS users_oauth_provider_id_idx ON users (oauth_provider, oauth_provider_id);

-- Location-based queries
CREATE INDEX IF NOT EXISTS users_location_idx ON users (location);

-- Full-text search (GIN indexes)
CREATE INDEX IF NOT EXISTS users_name_search_gin ON users USING gin(to_tsvector('english', first_name || ' ' || last_name));
CREATE INDEX IF NOT EXISTS users_bio_search_gin ON users USING gin(to_tsvector('english', COALESCE(bio, '')));
CREATE INDEX IF NOT EXISTS users_skills_search_gin ON users USING gin(to_tsvector('english', COALESCE(skills, '')));

-- Recent users (for "new members" feature)
CREATE INDEX IF NOT EXISTS users_created_at_idx ON users (created_at DESC);

-- =============================================================================
-- JOBS TABLE INDEXES
-- =============================================================================

-- Status-based filtering (most common query pattern)
CREATE INDEX IF NOT EXISTS jobs_status_idx ON jobs (status);
CREATE INDEX IF NOT EXISTS jobs_active_recent_idx ON jobs (created_at DESC) WHERE status = 'active';

-- Category and type filtering
CREATE INDEX IF NOT EXISTS jobs_category_idx ON jobs (category);
CREATE INDEX IF NOT EXISTS jobs_job_type_idx ON jobs (job_type);
CREATE INDEX IF NOT EXISTS jobs_category_status_idx ON jobs (category, status);

-- Location-based queries
CREATE INDEX IF NOT EXISTS jobs_location_idx ON jobs (location);
CREATE INDEX IF NOT EXISTS jobs_is_remote_idx ON jobs (is_remote) WHERE is_remote = true;

-- Salary range queries (for filtering by budget)
CREATE INDEX IF NOT EXISTS jobs_salary_range_idx ON jobs (salary_min, salary_max) WHERE status = 'active';
CREATE INDEX IF NOT EXISTS jobs_budget_idx ON jobs (budget) WHERE status = 'active';

-- Employer's jobs lookup
CREATE INDEX IF NOT EXISTS jobs_employer_id_idx ON jobs (employer_id, created_at DESC);

-- Full-text search (GIN indexes)
CREATE INDEX IF NOT EXISTS jobs_title_search_gin ON jobs USING gin(to_tsvector('english', title));
CREATE INDEX IF NOT EXISTS jobs_description_search_gin ON jobs USING gin(to_tsvector('english', description));
CREATE INDEX IF NOT EXISTS jobs_skills_search_gin ON jobs USING gin(to_tsvector('english', COALESCE(skills, '')));

-- Combined search (title + description)
CREATE INDEX IF NOT EXISTS jobs_combined_search_gin ON jobs USING gin(
    to_tsvector('english', title || ' ' || description || ' ' || COALESCE(skills, ''))
);

-- =============================================================================
-- MESSAGES TABLE INDEXES
-- =============================================================================

-- Conversation-based queries (most common)
CREATE INDEX IF NOT EXISTS messages_conversation_id_idx ON messages (conversation_id, created_at DESC);

-- Unread messages count (critical for notification badges)
CREATE INDEX IF NOT EXISTS messages_receiver_unread_idx ON messages (receiver_id, is_read) WHERE is_read = false;

-- Sender/receiver lookups
CREATE INDEX IF NOT EXISTS messages_sender_id_idx ON messages (sender_id, created_at DESC);
CREATE INDEX IF NOT EXISTS messages_receiver_id_idx ON messages (receiver_id, created_at DESC);

-- Message search (GIN index)
CREATE INDEX IF NOT EXISTS messages_content_search_gin ON messages USING gin(to_tsvector('english', content));

-- =============================================================================
-- CONVERSATIONS TABLE INDEXES
-- =============================================================================

-- Participant lookups
CREATE INDEX IF NOT EXISTS conversations_participant_1_idx ON conversations (participant_1_id);
CREATE INDEX IF NOT EXISTS conversations_participant_2_idx ON conversations (participant_2_id);
CREATE INDEX IF NOT EXISTS conversations_participants_idx ON conversations (participant_1_id, participant_2_id);

-- Recent conversations
CREATE INDEX IF NOT EXISTS conversations_updated_at_idx ON conversations (updated_at DESC);

-- =============================================================================
-- JOB APPLICATIONS TABLE INDEXES
-- =============================================================================

-- Job's applications
CREATE INDEX IF NOT EXISTS job_applications_job_id_idx ON job_applications (job_id, created_at DESC);

-- User's applications
CREATE INDEX IF NOT EXISTS job_applications_applicant_id_idx ON job_applications (applicant_id, created_at DESC);

-- Status filtering
CREATE INDEX IF NOT EXISTS job_applications_status_idx ON job_applications (status);
CREATE INDEX IF NOT EXISTS job_applications_pending_idx ON job_applications (status, created_at DESC) WHERE status = 'pending';

-- Prevent duplicate applications
CREATE UNIQUE INDEX IF NOT EXISTS job_applications_unique_idx ON job_applications (job_id, applicant_id);

-- =============================================================================
-- FOLLOWS TABLE INDEXES
-- =============================================================================

-- Follower/following lookups
CREATE INDEX IF NOT EXISTS follows_follower_id_idx ON follows (follower_id);
CREATE INDEX IF NOT EXISTS follows_followed_id_idx ON follows (followed_id);

-- Prevent duplicate follows
CREATE UNIQUE INDEX IF NOT EXISTS follows_unique_idx ON follows (follower_id, followed_id);

-- =============================================================================
-- NOTIFICATIONS TABLE INDEXES
-- =============================================================================

-- User's notifications (most common query)
CREATE INDEX IF NOT EXISTS notifications_user_id_idx ON notifications (user_id, created_at DESC);

-- Unread notifications count (critical for badge)
CREATE INDEX IF NOT EXISTS notifications_user_unread_idx ON notifications (user_id, is_read) WHERE is_read = false;

-- =============================================================================
-- POSTS TABLE INDEXES
-- =============================================================================

-- Feed query (recent posts)
CREATE INDEX IF NOT EXISTS posts_created_at_idx ON posts (created_at DESC);

-- User's posts
CREATE INDEX IF NOT EXISTS posts_user_id_idx ON posts (user_id, created_at DESC);

-- Post type filtering
CREATE INDEX IF NOT EXISTS posts_post_type_idx ON posts (post_type);

-- Job-related posts
CREATE INDEX IF NOT EXISTS posts_related_job_idx ON posts (related_job_id) WHERE related_job_id IS NOT NULL;

-- Full-text search (GIN index)
CREATE INDEX IF NOT EXISTS posts_content_search_gin ON posts USING gin(to_tsvector('english', content));

-- =============================================================================
-- POST LIKES TABLE INDEXES
-- =============================================================================

-- Post's likes
CREATE INDEX IF NOT EXISTS post_likes_post_id_idx ON post_likes (post_id);

-- User's likes
CREATE INDEX IF NOT EXISTS post_likes_user_id_idx ON post_likes (user_id);

-- Prevent duplicate likes
CREATE UNIQUE INDEX IF NOT EXISTS post_likes_unique_idx ON post_likes (user_id, post_id);

-- =============================================================================
-- POST COMMENTS TABLE INDEXES
-- =============================================================================

-- Post's comments
CREATE INDEX IF NOT EXISTS post_comments_post_id_idx ON post_comments (post_id, created_at ASC);

-- User's comments
CREATE INDEX IF NOT EXISTS post_comments_user_id_idx ON post_comments (user_id);

-- =============================================================================
-- REVIEWS TABLE INDEXES
-- =============================================================================

-- Reviewee's reviews (user's rating)
CREATE INDEX IF NOT EXISTS reviews_reviewee_id_idx ON reviews (reviewee_id);

-- Job's reviews
CREATE INDEX IF NOT EXISTS reviews_job_id_idx ON reviews (job_id);

-- Rating distribution
CREATE INDEX IF NOT EXISTS reviews_rating_idx ON reviews (rating);

-- =============================================================================
-- PROFILE PICTURES TABLE INDEXES
-- =============================================================================

-- User's pictures
CREATE INDEX IF NOT EXISTS profile_pictures_user_id_idx ON profile_pictures (user_id);

-- Current profile picture
CREATE INDEX IF NOT EXISTS profile_pictures_current_idx ON profile_pictures (user_id, is_current) WHERE is_current = true;

-- =============================================================================
-- INDEX MAINTENANCE QUERIES
-- =============================================================================

-- Analyze all tables (update statistics for query planner)
ANALYZE users;
ANALYZE jobs;
ANALYZE messages;
ANALYZE conversations;
ANALYZE job_applications;
ANALYZE follows;
ANALYZE notifications;
ANALYZE posts;
ANALYZE post_likes;
ANALYZE post_comments;
ANALYZE reviews;
ANALYZE profile_pictures;

-- =============================================================================
-- VERIFY INDEXES CREATED
-- =============================================================================

SELECT 
    schemaname,
    tablename,
    indexname,
    indexdef
FROM pg_indexes
WHERE schemaname = 'public'
ORDER BY tablename, indexname;
