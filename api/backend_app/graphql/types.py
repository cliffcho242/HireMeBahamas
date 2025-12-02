"""GraphQL types for HireMeBahamas API."""
from datetime import datetime
from typing import Optional, List

import strawberry


@strawberry.type
class UserType:
    """GraphQL type for User."""
    id: int
    email: str
    first_name: str
    last_name: str
    username: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    occupation: Optional[str] = None
    company_name: Optional[str] = None
    bio: Optional[str] = None
    skills: Optional[str] = None
    experience: Optional[str] = None
    education: Optional[str] = None
    avatar_url: Optional[str] = None
    is_available_for_hire: bool = False
    role: Optional[str] = None
    created_at: Optional[datetime] = None
    followers_count: int = 0
    following_count: int = 0


@strawberry.type
class PostAuthorType:
    """Minimal user type for post authors."""
    id: int
    first_name: str
    last_name: str
    username: Optional[str] = None
    avatar_url: Optional[str] = None
    occupation: Optional[str] = None


@strawberry.type
class PostType:
    """GraphQL type for Post."""
    id: int
    content: str
    image_url: Optional[str] = None
    video_url: Optional[str] = None
    post_type: str = "text"
    related_job_id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    likes_count: int = 0
    comments_count: int = 0
    is_liked: bool = False
    author: Optional[PostAuthorType] = None


@strawberry.type
class CommentAuthorType:
    """Minimal user type for comment authors."""
    id: int
    first_name: str
    last_name: str
    username: Optional[str] = None
    avatar_url: Optional[str] = None


@strawberry.type
class CommentType:
    """GraphQL type for Comment."""
    id: int
    post_id: int
    content: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    author: Optional[CommentAuthorType] = None


@strawberry.type
class MessageSenderType:
    """Minimal user type for message senders."""
    id: int
    first_name: str
    last_name: str
    avatar_url: Optional[str] = None


@strawberry.type
class MessageType:
    """GraphQL type for Message."""
    id: int
    content: str
    sender_id: int
    receiver_id: int
    conversation_id: int
    is_read: bool = False
    created_at: Optional[datetime] = None
    sender: Optional[MessageSenderType] = None


@strawberry.type
class ConversationParticipantType:
    """Minimal user type for conversation participants."""
    id: int
    first_name: str
    last_name: str
    avatar_url: Optional[str] = None


@strawberry.type
class ConversationType:
    """GraphQL type for Conversation."""
    id: int
    participant_1_id: int
    participant_2_id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    participant_1: Optional[ConversationParticipantType] = None
    participant_2: Optional[ConversationParticipantType] = None
    messages: List[MessageType] = strawberry.field(default_factory=list)
    last_message: Optional[MessageType] = None


@strawberry.type
class NotificationType:
    """GraphQL type for Notification."""
    id: int
    notification_type: str
    content: str
    related_id: Optional[int] = None
    is_read: bool = False
    created_at: Optional[datetime] = None
    actor: Optional[UserType] = None


@strawberry.type
class JobType:
    """GraphQL type for Job."""
    id: int
    title: str
    company: str
    description: str
    requirements: Optional[str] = None
    benefits: Optional[str] = None
    category: str
    job_type: str
    location: str
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    budget: Optional[float] = None
    budget_type: str = "fixed"
    is_remote: bool = False
    skills: Optional[str] = None
    status: str = "active"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    employer: Optional[PostAuthorType] = None


@strawberry.type
class FriendType:
    """GraphQL type for friend/connection."""
    id: int
    first_name: str
    last_name: str
    username: Optional[str] = None
    avatar_url: Optional[str] = None
    occupation: Optional[str] = None
    is_online: bool = False


# Edge and Connection types for Relay-style pagination
@strawberry.type
class PageInfo:
    """Pagination information for Relay-style connections."""
    has_next_page: bool
    has_previous_page: bool
    start_cursor: Optional[str] = None
    end_cursor: Optional[str] = None


@strawberry.type
class PostEdge:
    """Edge type for posts in a connection."""
    cursor: str
    node: PostType


@strawberry.type
class PostConnection:
    """Connection type for paginated posts (Relay-style)."""
    edges: List[PostEdge]
    page_info: PageInfo
    total_count: int


@strawberry.type
class MessageEdge:
    """Edge type for messages in a connection."""
    cursor: str
    node: MessageType


@strawberry.type
class MessageConnection:
    """Connection type for paginated messages (Relay-style)."""
    edges: List[MessageEdge]
    page_info: PageInfo
    total_count: int


@strawberry.type
class NotificationEdge:
    """Edge type for notifications in a connection."""
    cursor: str
    node: NotificationType


@strawberry.type
class NotificationConnection:
    """Connection type for paginated notifications (Relay-style)."""
    edges: List[NotificationEdge]
    page_info: PageInfo
    total_count: int


# Response types for mutations
@strawberry.type
class LikeResponse:
    """Response type for like mutation."""
    success: bool
    action: str  # "like" or "unlike"
    liked: bool
    likes_count: int


@strawberry.type
class FollowResponse:
    """Response type for follow mutation."""
    success: bool
    action: str  # "follow" or "unfollow"
    following: bool


@strawberry.type
class SendMessageResponse:
    """Response type for sendMessage mutation."""
    success: bool
    message: MessageType
