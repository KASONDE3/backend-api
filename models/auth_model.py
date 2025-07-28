from sqlalchemy import Column, Integer, String
from db import Base

class Auth(Base):
    __tablename__ = "auth"
    
    auth_id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
