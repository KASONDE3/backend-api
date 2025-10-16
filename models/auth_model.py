from sqlalchemy import Column, Integer, String, Boolean
from db import Base

class Auth(Base):
    __tablename__ = "auth"
    
    auth_id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    # Whether the account is allowed to login
    is_approved = Column(Boolean, nullable=False, server_default='0')
