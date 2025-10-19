from sqlalchemy import Column, String, DateTime, Text, Boolean, Integer, ForeignKey
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime

from app.database import Base


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    phone = Column(String(20))
    location = Column(String(200))
    bio = Column(Text)
    skills = Column(Text)  # Store as comma-separated text
    experience = Column(Text)
    education = Column(Text)
    avatar_url = Column(String(500))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    jobs_posted = relationship("Job", back_populates="employer")
    applications = relationship("JobApplication", back_populates="applicant")
    sent_messages = relationship("Message", back_populates="sender", 
                               foreign_keys="Message.sender_id")
    conversations_1 = relationship("Conversation", 
                                  back_populates="participant_1",
                                  foreign_keys="Conversation.participant_1_id")
    conversations_2 = relationship("Conversation", 
                                  back_populates="participant_2",
                                  foreign_keys="Conversation.participant_2_id")
    reviews_given = relationship("Review", back_populates="reviewer", 
                               foreign_keys="Review.reviewer_id")
    reviews_received = relationship("Review", back_populates="reviewee", 
                                  foreign_keys="Review.reviewee_id")
    
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
    job_type = Column(String(50), nullable=False, default='full-time')
    location = Column(String(200), nullable=False)
    salary_min = Column(Integer)
    salary_max = Column(Integer)
    status = Column(String(20), default='active')
    employer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    employer = relationship("User", back_populates="jobs_posted")
    applications = relationship("JobApplication", back_populates="job", 
                              cascade="all, delete-orphan")


class JobApplication(Base):
    __tablename__ = "job_applications"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    applicant_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    cover_letter = Column(Text)
    status = Column(String(20), default='pending')
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
    participant_1 = relationship("User", back_populates="conversations_1",
                                foreign_keys=[participant_1_id])
    participant_2 = relationship("User", back_populates="conversations_2",
                                foreign_keys=[participant_2_id])
    messages = relationship("Message", back_populates="conversation", 
                          cascade="all, delete-orphan")


class Message(Base):
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), 
                           nullable=False)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    conversation = relationship("Conversation", back_populates="messages")
    sender = relationship("User", back_populates="sent_messages")


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
    reviewer = relationship("User", back_populates="reviews_given",
                          foreign_keys=[reviewer_id])
    reviewee = relationship("User", back_populates="reviews_received",
                          foreign_keys=[reviewee_id])


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