from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from uuid import UUID


class MessageCreate(BaseModel):
    content: str


class UserInfo(BaseModel):
    id: str
    first_name: str
    last_name: str
    profile_image: Optional[str] = None
    
    class Config:
        from_attributes = True


class MessageResponse(BaseModel):
    id: str
    conversation_id: str
    sender_id: str
    receiver_id: str
    content: str
    is_read: bool
    created_at: datetime
    sender: UserInfo
    receiver: UserInfo
    
    class Config:
        from_attributes = True


class ConversationCreate(BaseModel):
    participant_id: UUID


class ConversationResponse(BaseModel):
    id: str
    participant_1_id: str
    participant_2_id: str
    participant_1: UserInfo
    participant_2: UserInfo
    messages: Optional[List[MessageResponse]] = None
    last_message: Optional[MessageResponse] = None
    unread_count: int = 0
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True