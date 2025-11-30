"""GraphQL resolvers for HireMeBahamas API."""
import base64
import logging
from typing import Optional, List

import strawberry
from strawberry.types import Info
from sqlalchemy import and_, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import (
    User, Post, PostLike, PostComment, Message, Conversation,
    Notification, Job, Follow
)
from app.graphql.types import (
    UserType, PostType, PostAuthorType, CommentType, CommentAuthorType,
    MessageType, MessageSenderType, ConversationType, ConversationParticipantType,
    NotificationType, JobType, FriendType,
    PostConnection, PostEdge, PageInfo,
    MessageConnection, MessageEdge,
    NotificationConnection, NotificationEdge,
    LikeResponse, FollowResponse, SendMessageResponse
)

logger = logging.getLogger(__name__)


def encode_cursor(id: int) -> str:
    """Encode an ID into a cursor for pagination."""
    return base64.b64encode(f"cursor:{id}".encode()).decode()


def decode_cursor(cursor: str) -> Optional[int]:
    """Decode a cursor back into an ID."""
    try:
        decoded = base64.b64decode(cursor.encode()).decode()
        if decoded.startswith("cursor:"):
            return int(decoded[7:])
    except (ValueError, UnicodeDecodeError):
        pass
    return None


def user_to_type(user: User) -> UserType:
    """Convert SQLAlchemy User to GraphQL UserType."""
    return UserType(
        id=user.id,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        username=user.username,
        phone=user.phone,
        location=user.location,
        occupation=user.occupation,
        company_name=user.company_name,
        bio=user.bio,
        skills=user.skills,
        experience=user.experience,
        education=user.education,
        avatar_url=user.avatar_url,
        is_available_for_hire=user.is_available_for_hire or False,
        role=user.role,
        created_at=user.created_at,
        followers_count=0,
        following_count=0,
    )


def user_to_post_author(user: User) -> PostAuthorType:
    """Convert SQLAlchemy User to GraphQL PostAuthorType."""
    return PostAuthorType(
        id=user.id,
        first_name=user.first_name,
        last_name=user.last_name,
        username=user.username,
        avatar_url=user.avatar_url,
        occupation=user.occupation,
    )


def user_to_comment_author(user: User) -> CommentAuthorType:
    """Convert SQLAlchemy User to GraphQL CommentAuthorType."""
    return CommentAuthorType(
        id=user.id,
        first_name=user.first_name,
        last_name=user.last_name,
        username=user.username,
        avatar_url=user.avatar_url,
    )


def user_to_message_sender(user: User) -> MessageSenderType:
    """Convert SQLAlchemy User to GraphQL MessageSenderType."""
    return MessageSenderType(
        id=user.id,
        first_name=user.first_name,
        last_name=user.last_name,
        avatar_url=user.avatar_url,
    )


def user_to_conversation_participant(user: User) -> ConversationParticipantType:
    """Convert SQLAlchemy User to GraphQL ConversationParticipantType."""
    return ConversationParticipantType(
        id=user.id,
        first_name=user.first_name,
        last_name=user.last_name,
        avatar_url=user.avatar_url,
    )


async def enrich_post(
    post: Post,
    db: AsyncSession,
    current_user_id: Optional[int] = None
) -> PostType:
    """Enrich a post with counts and like status."""
    # Get likes count
    likes_result = await db.execute(
        select(func.count()).select_from(PostLike).where(PostLike.post_id == post.id)
    )
    likes_count = likes_result.scalar() or 0

    # Get comments count
    comments_result = await db.execute(
        select(func.count()).select_from(PostComment).where(PostComment.post_id == post.id)
    )
    comments_count = comments_result.scalar() or 0

    # Check if current user liked this post
    is_liked = False
    if current_user_id:
        liked_result = await db.execute(
            select(PostLike).where(
                and_(PostLike.post_id == post.id, PostLike.user_id == current_user_id)
            )
        )
        is_liked = liked_result.scalar_one_or_none() is not None

    return PostType(
        id=post.id,
        content=post.content,
        image_url=post.image_url,
        video_url=post.video_url,
        post_type=post.post_type or "text",
        related_job_id=post.related_job_id,
        created_at=post.created_at,
        updated_at=post.updated_at,
        likes_count=likes_count,
        comments_count=comments_count,
        is_liked=is_liked,
        author=user_to_post_author(post.user) if post.user else None,
    )


async def get_user_follow_counts(user_id: int, db: AsyncSession) -> tuple[int, int]:
    """Get followers and following counts for a user."""
    followers_result = await db.execute(
        select(func.count()).select_from(Follow).where(Follow.followed_id == user_id)
    )
    followers_count = followers_result.scalar() or 0

    following_result = await db.execute(
        select(func.count()).select_from(Follow).where(Follow.follower_id == user_id)
    )
    following_count = following_result.scalar() or 0

    return followers_count, following_count


@strawberry.type
class Query:
    """GraphQL Query resolvers."""

    @strawberry.field
    async def me(self, info: Info) -> Optional[UserType]:
        """Get the current authenticated user."""
        context = info.context
        current_user = context.get("current_user")
        db: AsyncSession = context.get("db")
        
        if not current_user:
            return None
        
        followers_count, following_count = await get_user_follow_counts(current_user.id, db)
        
        user_type = user_to_type(current_user)
        user_type.followers_count = followers_count
        user_type.following_count = following_count
        
        return user_type

    @strawberry.field
    async def user(self, info: Info, id: int) -> Optional[UserType]:
        """Get a user by ID."""
        context = info.context
        db: AsyncSession = context.get("db")
        
        result = await db.execute(select(User).where(User.id == id))
        user = result.scalar_one_or_none()
        
        if not user:
            return None
        
        followers_count, following_count = await get_user_follow_counts(user.id, db)
        
        user_type = user_to_type(user)
        user_type.followers_count = followers_count
        user_type.following_count = following_count
        
        return user_type

    @strawberry.field
    async def posts(
        self,
        info: Info,
        first: int = 20,
        after: Optional[str] = None,
        user_id: Optional[int] = None,
    ) -> PostConnection:
        """Get posts feed with Relay-style pagination."""
        context = info.context
        db: AsyncSession = context.get("db")
        current_user = context.get("current_user")
        current_user_id = current_user.id if current_user else None

        # Build base query
        query = select(Post).options(selectinload(Post.user))
        
        if user_id:
            query = query.where(Post.user_id == user_id)
        
        # Apply cursor-based pagination
        if after:
            cursor_id = decode_cursor(after)
            if cursor_id:
                query = query.where(Post.id < cursor_id)
        
        query = query.order_by(desc(Post.id)).limit(first + 1)  # +1 to check if there's more
        
        result = await db.execute(query)
        posts = result.scalars().all()
        
        has_next_page = len(posts) > first
        if has_next_page:
            posts = posts[:first]
        
        # Build edges
        edges = []
        for post in posts:
            if post.user:
                post_type = await enrich_post(post, db, current_user_id)
                edges.append(PostEdge(
                    cursor=encode_cursor(post.id),
                    node=post_type,
                ))
        
        # Get total count
        count_query = select(func.count()).select_from(Post)
        if user_id:
            count_query = count_query.where(Post.user_id == user_id)
        count_result = await db.execute(count_query)
        total_count = count_result.scalar() or 0
        
        return PostConnection(
            edges=edges,
            page_info=PageInfo(
                has_next_page=has_next_page,
                has_previous_page=after is not None,
                start_cursor=edges[0].cursor if edges else None,
                end_cursor=edges[-1].cursor if edges else None,
            ),
            total_count=total_count,
        )

    @strawberry.field
    async def messages(
        self,
        info: Info,
        conversation_id: int,
        first: int = 50,
        after: Optional[str] = None,
    ) -> MessageConnection:
        """Get messages for a conversation with Relay-style pagination."""
        context = info.context
        db: AsyncSession = context.get("db")
        current_user = context.get("current_user")
        
        if not current_user:
            return MessageConnection(
                edges=[],
                page_info=PageInfo(has_next_page=False, has_previous_page=False),
                total_count=0,
            )
        
        # Verify user is part of conversation
        conv_result = await db.execute(
            select(Conversation).where(Conversation.id == conversation_id)
        )
        conversation = conv_result.scalar_one_or_none()
        
        if not conversation:
            return MessageConnection(
                edges=[],
                page_info=PageInfo(has_next_page=False, has_previous_page=False),
                total_count=0,
            )
        
        if conversation.participant_1_id != current_user.id and conversation.participant_2_id != current_user.id:
            return MessageConnection(
                edges=[],
                page_info=PageInfo(has_next_page=False, has_previous_page=False),
                total_count=0,
            )
        
        # Build query
        query = (
            select(Message)
            .options(selectinload(Message.sender))
            .where(Message.conversation_id == conversation_id)
        )
        
        if after:
            cursor_id = decode_cursor(after)
            if cursor_id:
                query = query.where(Message.id > cursor_id)
        
        query = query.order_by(Message.id).limit(first + 1)
        
        result = await db.execute(query)
        messages = result.scalars().all()
        
        has_next_page = len(messages) > first
        if has_next_page:
            messages = messages[:first]
        
        # Build edges
        edges = []
        for msg in messages:
            edges.append(MessageEdge(
                cursor=encode_cursor(msg.id),
                node=MessageType(
                    id=msg.id,
                    content=msg.content,
                    sender_id=msg.sender_id,
                    receiver_id=msg.receiver_id,
                    conversation_id=msg.conversation_id,
                    is_read=msg.is_read or False,
                    created_at=msg.created_at,
                    sender=user_to_message_sender(msg.sender) if msg.sender else None,
                ),
            ))
        
        # Get total count
        count_result = await db.execute(
            select(func.count()).select_from(Message).where(Message.conversation_id == conversation_id)
        )
        total_count = count_result.scalar() or 0
        
        return MessageConnection(
            edges=edges,
            page_info=PageInfo(
                has_next_page=has_next_page,
                has_previous_page=after is not None,
                start_cursor=edges[0].cursor if edges else None,
                end_cursor=edges[-1].cursor if edges else None,
            ),
            total_count=total_count,
        )

    @strawberry.field
    async def conversations(self, info: Info) -> List[ConversationType]:
        """Get all conversations for the current user."""
        context = info.context
        db: AsyncSession = context.get("db")
        current_user = context.get("current_user")
        
        if not current_user:
            return []
        
        # Get conversations where user is a participant
        query = (
            select(Conversation)
            .options(
                selectinload(Conversation.participant_1),
                selectinload(Conversation.participant_2),
                selectinload(Conversation.messages).selectinload(Message.sender),
            )
            .where(
                (Conversation.participant_1_id == current_user.id) |
                (Conversation.participant_2_id == current_user.id)
            )
            .order_by(desc(Conversation.updated_at))
        )
        
        result = await db.execute(query)
        conversations = result.scalars().all()
        
        conv_types = []
        for conv in conversations:
            # Get last message
            last_message = None
            if conv.messages:
                last_msg = conv.messages[-1]
                last_message = MessageType(
                    id=last_msg.id,
                    content=last_msg.content,
                    sender_id=last_msg.sender_id,
                    receiver_id=last_msg.receiver_id,
                    conversation_id=last_msg.conversation_id,
                    is_read=last_msg.is_read or False,
                    created_at=last_msg.created_at,
                    sender=user_to_message_sender(last_msg.sender) if last_msg.sender else None,
                )
            
            conv_types.append(ConversationType(
                id=conv.id,
                participant_1_id=conv.participant_1_id,
                participant_2_id=conv.participant_2_id,
                created_at=conv.created_at,
                updated_at=conv.updated_at,
                participant_1=user_to_conversation_participant(conv.participant_1) if conv.participant_1 else None,
                participant_2=user_to_conversation_participant(conv.participant_2) if conv.participant_2 else None,
                messages=[
                    MessageType(
                        id=m.id,
                        content=m.content,
                        sender_id=m.sender_id,
                        receiver_id=m.receiver_id,
                        conversation_id=m.conversation_id,
                        is_read=m.is_read or False,
                        created_at=m.created_at,
                        sender=user_to_message_sender(m.sender) if m.sender else None,
                    ) for m in conv.messages
                ],
                last_message=last_message,
            ))
        
        return conv_types

    @strawberry.field
    async def notifications(
        self,
        info: Info,
        first: int = 20,
        after: Optional[str] = None,
        unread_only: bool = False,
    ) -> NotificationConnection:
        """Get notifications with Relay-style pagination."""
        context = info.context
        db: AsyncSession = context.get("db")
        current_user = context.get("current_user")
        
        if not current_user:
            return NotificationConnection(
                edges=[],
                page_info=PageInfo(has_next_page=False, has_previous_page=False),
                total_count=0,
            )
        
        # Build query
        query = (
            select(Notification)
            .options(selectinload(Notification.actor))
            .where(Notification.user_id == current_user.id)
        )
        
        if unread_only:
            query = query.where(Notification.is_read == False)
        
        if after:
            cursor_id = decode_cursor(after)
            if cursor_id:
                query = query.where(Notification.id < cursor_id)
        
        query = query.order_by(desc(Notification.id)).limit(first + 1)
        
        result = await db.execute(query)
        notifications = result.scalars().all()
        
        has_next_page = len(notifications) > first
        if has_next_page:
            notifications = notifications[:first]
        
        # Build edges
        edges = []
        for notif in notifications:
            actor_type = None
            if notif.actor:
                actor_type = user_to_type(notif.actor)
            
            edges.append(NotificationEdge(
                cursor=encode_cursor(notif.id),
                node=NotificationType(
                    id=notif.id,
                    notification_type=notif.notification_type.value if notif.notification_type else "unknown",
                    content=notif.content,
                    related_id=notif.related_id,
                    is_read=notif.is_read or False,
                    created_at=notif.created_at,
                    actor=actor_type,
                ),
            ))
        
        # Get total count
        count_query = select(func.count()).select_from(Notification).where(
            Notification.user_id == current_user.id
        )
        if unread_only:
            count_query = count_query.where(Notification.is_read == False)
        count_result = await db.execute(count_query)
        total_count = count_result.scalar() or 0
        
        return NotificationConnection(
            edges=edges,
            page_info=PageInfo(
                has_next_page=has_next_page,
                has_previous_page=after is not None,
                start_cursor=edges[0].cursor if edges else None,
                end_cursor=edges[-1].cursor if edges else None,
            ),
            total_count=total_count,
        )

    @strawberry.field
    async def friends(self, info: Info) -> List[FriendType]:
        """Get friends (mutual follows) for the current user."""
        context = info.context
        db: AsyncSession = context.get("db")
        current_user = context.get("current_user")
        
        if not current_user:
            return []
        
        # Get users that the current user follows
        following_result = await db.execute(
            select(Follow.followed_id).where(Follow.follower_id == current_user.id)
        )
        following_ids = [row[0] for row in following_result.fetchall()]
        
        if not following_ids:
            return []
        
        # Get users that also follow back (mutual follows = friends)
        friends_result = await db.execute(
            select(User)
            .join(Follow, and_(
                Follow.follower_id == User.id,
                Follow.followed_id == current_user.id
            ))
            .where(User.id.in_(following_ids))
        )
        friends = friends_result.scalars().all()
        
        return [
            FriendType(
                id=f.id,
                first_name=f.first_name,
                last_name=f.last_name,
                username=f.username,
                avatar_url=f.avatar_url,
                occupation=f.occupation,
                is_online=False,  # Would need real-time presence tracking
            )
            for f in friends
        ]

    @strawberry.field
    async def post_comments(
        self,
        info: Info,
        post_id: int,
    ) -> List[CommentType]:
        """Get comments for a post."""
        context = info.context
        db: AsyncSession = context.get("db")
        
        result = await db.execute(
            select(PostComment)
            .options(selectinload(PostComment.user))
            .where(PostComment.post_id == post_id)
            .order_by(PostComment.created_at)
        )
        comments = result.scalars().all()
        
        return [
            CommentType(
                id=c.id,
                post_id=c.post_id,
                content=c.content,
                created_at=c.created_at,
                updated_at=c.updated_at,
                author=user_to_comment_author(c.user) if c.user else None,
            )
            for c in comments
        ]


@strawberry.type
class Mutation:
    """GraphQL Mutation resolvers."""

    @strawberry.mutation
    async def like_post(self, info: Info, post_id: int) -> LikeResponse:
        """Toggle like on a post."""
        context = info.context
        db: AsyncSession = context.get("db")
        current_user = context.get("current_user")
        
        if not current_user:
            return LikeResponse(success=False, action="error", liked=False, likes_count=0)
        
        # Check if post exists
        post_result = await db.execute(select(Post).where(Post.id == post_id))
        post = post_result.scalar_one_or_none()
        
        if not post:
            return LikeResponse(success=False, action="error", liked=False, likes_count=0)
        
        # Check if already liked
        like_result = await db.execute(
            select(PostLike).where(
                and_(PostLike.post_id == post_id, PostLike.user_id == current_user.id)
            )
        )
        existing_like = like_result.scalar_one_or_none()
        
        if existing_like:
            await db.delete(existing_like)
            await db.commit()
            action = "unlike"
            liked = False
        else:
            new_like = PostLike(post_id=post_id, user_id=current_user.id)
            db.add(new_like)
            await db.commit()
            action = "like"
            liked = True
        
        # Get updated likes count
        likes_result = await db.execute(
            select(func.count()).select_from(PostLike).where(PostLike.post_id == post_id)
        )
        likes_count = likes_result.scalar() or 0
        
        return LikeResponse(success=True, action=action, liked=liked, likes_count=likes_count)

    @strawberry.mutation
    async def follow_user(self, info: Info, user_id: int) -> FollowResponse:
        """Toggle follow on a user."""
        context = info.context
        db: AsyncSession = context.get("db")
        current_user = context.get("current_user")
        
        if not current_user:
            return FollowResponse(success=False, action="error", following=False)
        
        if current_user.id == user_id:
            return FollowResponse(success=False, action="error", following=False)
        
        # Check if user exists
        user_result = await db.execute(select(User).where(User.id == user_id))
        target_user = user_result.scalar_one_or_none()
        
        if not target_user:
            return FollowResponse(success=False, action="error", following=False)
        
        # Check if already following
        follow_result = await db.execute(
            select(Follow).where(
                and_(Follow.follower_id == current_user.id, Follow.followed_id == user_id)
            )
        )
        existing_follow = follow_result.scalar_one_or_none()
        
        if existing_follow:
            await db.delete(existing_follow)
            await db.commit()
            action = "unfollow"
            following = False
        else:
            new_follow = Follow(follower_id=current_user.id, followed_id=user_id)
            db.add(new_follow)
            await db.commit()
            action = "follow"
            following = True
        
        return FollowResponse(success=True, action=action, following=following)

    @strawberry.mutation
    async def send_message(
        self,
        info: Info,
        conversation_id: int,
        content: str,
    ) -> SendMessageResponse:
        """Send a message in a conversation."""
        context = info.context
        db: AsyncSession = context.get("db")
        current_user = context.get("current_user")
        
        if not current_user:
            return SendMessageResponse(
                success=False,
                message=MessageType(
                    id=0, content="", sender_id=0, receiver_id=0, conversation_id=0
                )
            )
        
        # Verify conversation exists and user is participant
        conv_result = await db.execute(
            select(Conversation).where(Conversation.id == conversation_id)
        )
        conversation = conv_result.scalar_one_or_none()
        
        if not conversation:
            return SendMessageResponse(
                success=False,
                message=MessageType(
                    id=0, content="", sender_id=0, receiver_id=0, conversation_id=0
                )
            )
        
        if conversation.participant_1_id != current_user.id and conversation.participant_2_id != current_user.id:
            return SendMessageResponse(
                success=False,
                message=MessageType(
                    id=0, content="", sender_id=0, receiver_id=0, conversation_id=0
                )
            )
        
        # Determine receiver
        receiver_id = (
            conversation.participant_2_id
            if conversation.participant_1_id == current_user.id
            else conversation.participant_1_id
        )
        
        # Create message
        new_message = Message(
            conversation_id=conversation_id,
            sender_id=current_user.id,
            receiver_id=receiver_id,
            content=content,
        )
        db.add(new_message)
        await db.commit()
        await db.refresh(new_message)
        
        # Load sender
        await db.refresh(new_message, ["sender"])
        
        return SendMessageResponse(
            success=True,
            message=MessageType(
                id=new_message.id,
                content=new_message.content,
                sender_id=new_message.sender_id,
                receiver_id=new_message.receiver_id,
                conversation_id=new_message.conversation_id,
                is_read=new_message.is_read or False,
                created_at=new_message.created_at,
                sender=user_to_message_sender(current_user),
            )
        )

    @strawberry.mutation
    async def mark_notification_read(
        self,
        info: Info,
        notification_id: int,
    ) -> bool:
        """Mark a notification as read."""
        context = info.context
        db: AsyncSession = context.get("db")
        current_user = context.get("current_user")
        
        if not current_user:
            return False
        
        result = await db.execute(
            select(Notification).where(
                and_(
                    Notification.id == notification_id,
                    Notification.user_id == current_user.id
                )
            )
        )
        notification = result.scalar_one_or_none()
        
        if not notification:
            return False
        
        notification.is_read = True
        await db.commit()
        
        return True

    @strawberry.mutation
    async def mark_all_notifications_read(self, info: Info) -> bool:
        """Mark all notifications as read for the current user."""
        context = info.context
        db: AsyncSession = context.get("db")
        current_user = context.get("current_user")
        
        if not current_user:
            return False
        
        result = await db.execute(
            select(Notification).where(
                and_(
                    Notification.user_id == current_user.id,
                    Notification.is_read == False
                )
            )
        )
        notifications = result.scalars().all()
        
        for notif in notifications:
            notif.is_read = True
        
        await db.commit()
        
        return True
