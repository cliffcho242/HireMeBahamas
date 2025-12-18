from app.database import Base
from sqlalchemy import Boolean, Column, DateTime, Enum as SQLEnum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum


# Notification type enum
class NotificationType(str, enum.Enum):
    FOLLOW = "follow"
    JOB_APPLICATION = "job_application"
    JOB_POST = "job_post"
    LIKE = "like"
    COMMENT = "comment"
    MENTION = "mention"
    MESSAGE = "message"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=True)  # Nullable for OAuth users
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    username = Column(
        String(50), unique=True, index=True
    )  # Unique username for @mentions
    phone = Column(String(20))
    location = Column(String(200))
    occupation = Column(String(200))  # Job title or skill
    company_name = Column(String(200))  # Company name for employers/businesses
    bio = Column(Text)
    skills = Column(Text)  # Store as comma-separated text
    experience = Column(Text)
    education = Column(Text)
    avatar_url = Column(String(500))
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    is_available_for_hire = Column(Boolean, default=False)  # HireMe availability status
    role = Column(String(50), default="user")  # user, admin, employer, freelancer
    # OAuth fields
    oauth_provider = Column(String(50))  # 'google', 'apple', or None for regular accounts
    oauth_provider_id = Column(String(255))  # ID from OAuth provider
    # Monetization fields
    stripe_customer_id = Column(String(255), unique=True, index=True)  # Stripe customer ID
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    jobs_posted = relationship("Job", back_populates="employer")
    applications = relationship("JobApplication", back_populates="applicant")
    sent_messages = relationship(
        "Message",
        back_populates="sender",
        foreign_keys="Message.sender_id"
    )
    received_messages = relationship(
        "Message",
        foreign_keys="Message.receiver_id",
        overlaps="receiver"
    )
    conversations_1 = relationship(
        "Conversation",
        back_populates="participant_1",
        foreign_keys="Conversation.participant_1_id",
    )
    conversations_2 = relationship(
        "Conversation",
        back_populates="participant_2",
        foreign_keys="Conversation.participant_2_id",
    )
    reviews_given = relationship(
        "Review", back_populates="reviewer", foreign_keys="Review.reviewer_id"
    )
    reviews_received = relationship(
        "Review", back_populates="reviewee", foreign_keys="Review.reviewee_id"
    )
    following = relationship(
        "Follow",
        back_populates="follower",
        foreign_keys="Follow.follower_id",
    )
    followers = relationship(
        "Follow",
        back_populates="followed",
        foreign_keys="Follow.followed_id",
    )

    @hybrid_property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    company = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    requirements = Column(Text)
    benefits = Column(Text)
    category = Column(String(100), nullable=False)
    job_type = Column(String(50), nullable=False, default="full-time")
    location = Column(String(200), nullable=False)
    salary_min = Column(Integer)
    salary_max = Column(Integer)
    budget = Column(Float)  # Budget amount for the job
    budget_type = Column(String(20), default="fixed")  # fixed or hourly
    is_remote = Column(Boolean, default=False)  # Whether job is remote
    skills = Column(Text)  # Required skills as comma-separated text
    status = Column(String(20), default="active")
    # Monetization fields
    is_featured = Column(Boolean, default=False)  # Featured/paid job post
    is_sponsored = Column(Boolean, default=False)  # Sponsored ad placement
    featured_until = Column(DateTime(timezone=True), nullable=True)  # When featured expires
    employer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    employer = relationship("User", back_populates="jobs_posted")
    applications = relationship(
        "JobApplication", back_populates="job", cascade="all, delete-orphan"
    )


class JobApplication(Base):
    __tablename__ = "job_applications"

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    applicant_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    cover_letter = Column(Text)
    proposed_budget = Column(Float)  # Proposed budget amount by applicant
    status = Column(String(20), default="pending")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    job = relationship("Job", back_populates="applications")
    applicant = relationship("User", back_populates="applications")


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    participant_1_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    participant_2_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    participant_1 = relationship(
        "User", back_populates="conversations_1", foreign_keys=[participant_1_id]
    )
    participant_2 = relationship(
        "User", back_populates="conversations_2", foreign_keys=[participant_2_id]
    )
    messages = relationship(
        "Message", back_populates="conversation", cascade="all, delete-orphan"
    )


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    receiver_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    conversation = relationship("Conversation", back_populates="messages")
    sender = relationship("User", back_populates="sent_messages", foreign_keys=[sender_id])
    receiver = relationship("User", foreign_keys=[receiver_id])



class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    reviewer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    reviewee_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    rating = Column(Integer, nullable=False)  # 1-5 stars
    comment = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    job = relationship("Job")
    reviewer = relationship(
        "User", back_populates="reviews_given", foreign_keys=[reviewer_id]
    )
    reviewee = relationship(
        "User", back_populates="reviews_received", foreign_keys=[reviewee_id]
    )


class UploadedFile(Base):
    __tablename__ = "uploaded_files"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    file_type = Column(String(50), nullable=False)
    file_size = Column(Integer, nullable=False)
    file_url = Column(String(500), nullable=False)
    upload_type = Column(String(50), nullable=False)  # avatar, document, portfolio
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User")


class Follow(Base):
    __tablename__ = "follows"

    id = Column(Integer, primary_key=True, autoincrement=True)
    follower_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    followed_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    follower = relationship("User", back_populates="following", foreign_keys=[follower_id])
    followed = relationship("User", back_populates="followers", foreign_keys=[followed_id])


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    actor_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    notification_type = Column(SQLEnum(NotificationType), nullable=False)  # Type from NotificationType enum
    content = Column(Text, nullable=False)
    related_id = Column(Integer, nullable=True)  # ID of related job, post, etc.
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    actor = relationship("User", foreign_keys=[actor_id])


class ProfilePicture(Base):
    __tablename__ = "profile_pictures"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    file_url = Column(String(500), nullable=False)
    filename = Column(String(255), nullable=False)
    file_size = Column(Integer, nullable=False)
    is_current = Column(Boolean, default=False)  # Whether this is the active profile picture
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User")


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    image_url = Column(String(500))
    video_url = Column(String(500))
    post_type = Column(String(50), default="text")  # text, job, image, video
    related_job_id = Column(Integer, ForeignKey("jobs.id"), nullable=True)  # Link to job if this is a job post
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User")
    related_job = relationship("Job")
    likes = relationship("PostLike", back_populates="post", cascade="all, delete-orphan")
    comments = relationship("PostComment", back_populates="post", cascade="all, delete-orphan")


class PostLike(Base):
    __tablename__ = "post_likes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User")
    post = relationship("Post", back_populates="likes")


class PostComment(Base):
    __tablename__ = "post_comments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    post = relationship("Post", back_populates="comments")
    user = relationship("User")


class LoginAttempt(Base):
    """Track login attempts for security monitoring and analytics"""
    __tablename__ = "login_attempts"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Nullable for failed attempts with unknown user
    email_attempted = Column(String(255), nullable=False, index=True)  # Track attempted email
    ip_address = Column(String(45), nullable=True)  # IPv4 or IPv6
    success = Column(Boolean, nullable=False, default=False)
    failure_reason = Column(String(255), nullable=True)  # Error message for failed attempts
    user_agent = Column(String(500), nullable=True)  # Browser/device info
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id])


# ============================================================================
# MONETIZATION MODELS - Subscription, Payments, Boosts
# ============================================================================

class SubscriptionTier(Base):
    """Subscription tier definitions (Free, Pro, Business, Enterprise)"""
    __tablename__ = "subscription_tiers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False, unique=True)  # free, pro, business, enterprise
    display_name = Column(String(100), nullable=False)  # Display name for UI
    price = Column(Float, nullable=False, default=0)  # Monthly price in USD
    annual_price = Column(Float, nullable=True)  # Annual price (if different)
    billing_period = Column(String(20), default="monthly")  # monthly, annual
    description = Column(Text)
    features = Column(Text)  # JSON string of features
    limits = Column(Text)  # JSON string of usage limits
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    subscriptions = relationship("UserSubscription", back_populates="tier")


class UserSubscription(Base):
    """User subscription records linked to Stripe"""
    __tablename__ = "user_subscriptions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    tier_id = Column(Integer, ForeignKey("subscription_tiers.id"), nullable=False)
    stripe_subscription_id = Column(String(255), unique=True, index=True)
    stripe_customer_id = Column(String(255), index=True)
    status = Column(String(50), default="active")  # active, canceled, past_due, trialing, incomplete
    current_period_start = Column(DateTime(timezone=True))
    current_period_end = Column(DateTime(timezone=True))
    cancel_at_period_end = Column(Boolean, default=False)
    trial_end = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User")
    tier = relationship("SubscriptionTier", back_populates="subscriptions")
    payments = relationship("Payment", back_populates="subscription")


class Payment(Base):
    """Payment transaction history"""
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    subscription_id = Column(Integer, ForeignKey("user_subscriptions.id"), nullable=True)
    stripe_payment_id = Column(String(255), unique=True, index=True)
    stripe_invoice_id = Column(String(255), index=True)
    amount = Column(Float, nullable=False)
    currency = Column(String(3), default="USD")
    status = Column(String(50), nullable=False)  # succeeded, failed, pending, refunded
    payment_method = Column(String(50))  # card, bank_transfer
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User")
    subscription = relationship("UserSubscription", back_populates="payments")


class FeatureUsage(Base):
    """Track feature usage for subscription limits"""
    __tablename__ = "feature_usage"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    feature = Column(String(100), nullable=False)  # messages, posts, inmails, job_posts
    usage_count = Column(Integer, default=0)
    period_start = Column(DateTime(timezone=True), nullable=False)
    period_end = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User")


class BoostedPost(Base):
    """Boosted posts for enhanced visibility"""
    __tablename__ = "boosted_posts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    boost_duration_days = Column(Integer, default=7)  # How many days to boost
    boost_start = Column(DateTime(timezone=True), nullable=False)
    boost_end = Column(DateTime(timezone=True), nullable=False)
    amount_paid = Column(Float, nullable=False)  # Amount paid for boost
    payment_id = Column(Integer, ForeignKey("payments.id"), nullable=True)
    status = Column(String(20), default="active")  # active, expired, cancelled
    impressions = Column(Integer, default=0)  # Track views
    clicks = Column(Integer, default=0)  # Track clicks
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    post = relationship("Post")
    user = relationship("User")
    payment = relationship("Payment")


class SponsoredContent(Base):
    """Sponsored job posts and profile promotions (ads)"""
    __tablename__ = "sponsored_content"

    id = Column(Integer, primary_key=True, autoincrement=True)
    sponsor_user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    content_type = Column(String(50), nullable=False)  # job, profile, post
    content_id = Column(Integer, nullable=False)  # ID of the job, user profile, or post
    campaign_name = Column(String(200))
    budget = Column(Float, nullable=False)  # Total budget for campaign
    cost_per_click = Column(Float)  # CPC if using CPC model
    cost_per_impression = Column(Float)  # CPM if using CPM model
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=False)
    status = Column(String(20), default="active")  # active, paused, completed, cancelled
    impressions = Column(Integer, default=0)
    clicks = Column(Integer, default=0)
    conversions = Column(Integer, default=0)  # Applications, follows, etc.
    amount_spent = Column(Float, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    sponsor = relationship("User")


class AnalyticsEvent(Base):
    """Track user events for analytics (conversion, paywall views, etc.)"""
    __tablename__ = "analytics_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)  # Nullable for anonymous
    event_type = Column(String(100), nullable=False, index=True)  # upgrade_clicked, paywall_viewed, etc.
    event_data = Column(Text)  # JSON string of additional event data
    session_id = Column(String(255), index=True)
    ip_address = Column(String(45))
    user_agent = Column(String(500))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # Relationships
    user = relationship("User")
