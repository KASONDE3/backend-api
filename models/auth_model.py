from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from models.ticketModels import Base  # Reuse the global Base from ticketModels

class Auth(Base):
    __tablename__ = "auth"
    
    auth_id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), ForeignKey("users.email"), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    
    user = relationship("User", backref="auth_entry")
