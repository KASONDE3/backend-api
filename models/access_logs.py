from sqlalchemy import Column, Integer, String, DateTime, Index
from sqlalchemy.sql import func
from db import Base

class AccessLog(Base):
    __tablename__ = "access_logs"
    
    log_id = Column(Integer, primary_key=True, index=True)
    user_email = Column(String(255), nullable=False, index=True)
    action = Column(String(20), nullable=False)  # 'login' or 'logout'
    timestamp = Column(DateTime, server_default=func.now(), nullable=False, index=True)
    ip_address = Column(String(45), nullable=True)  # IPv4 or IPv6
    user_agent = Column(String(500), nullable=True)
    
    # Indexes for better query performance
    __table_args__ = (
        Index('idx_user_action', 'user_email', 'action'),
        Index('idx_timestamp', 'timestamp'),
        Index('idx_user_time', 'user_email', 'timestamp'),
    )
