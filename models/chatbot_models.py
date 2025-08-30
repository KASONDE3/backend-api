import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from sqlalchemy import Column, Integer, String, Text, DateTime, Index
from sqlalchemy.sql import func
from db import Base

# --- SQLAlchemy Model ---

class ChatbotConversation(Base):
    __tablename__ = "chatbot_conversations"
    
    conversation_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(255), nullable=True, index=True)  # Can be null for anonymous users
    message = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    confidence = Column(String(20), nullable=False)  # high/medium/low
    recommendation = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), index=True)
    
    # Index for better query performance
    __table_args__ = (
        Index('idx_user_time', 'user_id', 'created_at'),
        Index('idx_time', 'created_at'),
    )

# --- Pydantic Schemas ---

class ChatbotConversationCreate(BaseModel):
    user_id: Optional[str] = None
    message: str
    response: str
    confidence: str
    recommendation: Optional[str] = None

class ChatbotConversationOut(BaseModel):
    conversation_id: int
    user_id: Optional[str]
    message: str
    response: str
    confidence: str
    recommendation: Optional[str]
    created_at: datetime.datetime
    
    model_config = ConfigDict(from_attributes=True)

class ChatbotConversationSummary(BaseModel):
    total_conversations: int
    conversations_by_user: dict
    recent_conversations: list[ChatbotConversationOut]
