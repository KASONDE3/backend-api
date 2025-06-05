from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True)
    first_name = Column(String(255))
    other_name = Column(String(255), nullable=True)
    last_name = Column(String(255))
    nrc = Column(String(255))
    role = Column(String(20), nullable=False)
    department = Column(String(20), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now(), server_default=func.now())

class Ticket(Base):
    __tablename__ = "tickets"
    ticket_id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255))
    description = Column(Text)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    status_id = Column(Integer, ForeignKey("statuses.status_id"))
    category_id = Column(Integer, ForeignKey("ticket_categories.category_id"))
    priority_id = Column(Integer, ForeignKey("ticket_priorities.priority_id"))
    assigned_to = Column(Integer, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now(), server_default=func.now())

class TicketCategory(Base):
    __tablename__="ticket_categories"
    category_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True)
    
class TicketPriority(Base):
    __tablename__="ticket_priorities"
    priority_id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    response_time = Column(Integer, nullable=False)
    
class Status(Base):
    __tablename__="statuses"
    status_id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)

class TicketStatusUpdate(BaseModel):
    status_id: int