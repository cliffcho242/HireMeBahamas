"""
Central models import file for Alembic migrations.

This file imports all SQLAlchemy models to ensure they are registered
with Base.metadata before Alembic runs migrations.
"""

# Import Base first
from app.database import Base  # noqa: F401

# Import all model classes to register them with Base.metadata
# This ensures Alembic can auto-generate migrations correctly
try:
    # Import from backend.app.models (primary location)
    from backend.app.models import (
        User,
        Job,
        JobApplication,
        Post,
        PostLike,
        PostComment,
        Follow,
        Message,
        Notification,
        NotificationType,
        Conversation,
        Review,
        UploadedFile,
        ProfilePicture,
        LoginAttempt,
    )
    
    # Import RefreshToken from api.backend_app.models
    from api.backend_app.models import RefreshToken
    
    __all__ = [
        'Base',
        'User',
        'Job',
        'JobApplication',
        'Post',
        'PostLike',
        'PostComment',
        'Follow',
        'Message',
        'Notification',
        'NotificationType',
        'Conversation',
        'Review',
        'UploadedFile',
        'ProfilePicture',
        'LoginAttempt',
        'RefreshToken',
    ]
except ImportError as e:
    # If models can't be imported, log warning but don't fail
    import logging
    logger = logging.getLogger(__name__)
    logger.warning(f"Could not import all models: {e}")
    logger.warning("Alembic migrations may not work correctly without models")
    
    # At minimum, export Base
    __all__ = ['Base']
