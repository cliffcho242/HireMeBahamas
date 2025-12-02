from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class MessageCreate(BaseModel):
    content: str


class UserInfo(BaseModel):
    id: int
    first_name: str
    last_name: str
    profile_image: Optional[str] = None
    avatar_url: Optional[str] = None

    class Config:
        from_attributes = True


class MessageResponse(BaseModel):
    id: int
    conversation_id: int
    sender_id: int
    receiver_id: int
    content: str
    is_read: bool
    created_at: datetime
    sender: UserInfo
    receiver: UserInfo

    class Config:
        from_attributes = True


class ConversationCreate(BaseModel):
    participant_id: int


class ConversationResponse(BaseModel):
    id: int
    participant_1_id: int
    participant_2_id: int
    participant_1: UserInfo
    participant_2: UserInfo
    messages: Optional[List[MessageResponse]] = None
    last_message: Optional[MessageResponse] = None
    unread_count: int = 0
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
