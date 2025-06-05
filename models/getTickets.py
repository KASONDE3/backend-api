from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from db import Base

class User(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255))
    email = Column(String(255), unique=True, index=True)
    tickets = relationship("Ticket", back_populates="user")
    category = relationship("Category", back_populates="tickets")

class Priority(Base):
    __tablename__ = "ticket_priorities"
    priority_id = Column(Integer, primary_key=True)
    name = Column(String(100))
    tickets = relationship("Ticket", back_populates="priority")

class Status(Base):
    __tablename__ = "statuses"
    status_id = Column(Integer, primary_key=True)
    state = Column(String(100))
    tickets = relationship("Ticket", back_populates="status")

class Ticket(Base):
    __tablename__ = "tickets"
    ticket_id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255))
    description = Column(Text)
    category_id = Column(Integer, ForeignKey("ticket_categories.category_id"))
    priority_id = Column(Integer, ForeignKey("ticket_priorities.priority_id"))
    status_id = Column(Integer, ForeignKey("statuses.status_id"))
    user_id = Column(Integer, ForeignKey("users.user_id"))
    assigned_to = Column(Integer)

    category = relationship("Category", back_populates="tickets")
    priority = relationship("Priority", back_populates="tickets")
    status = relationship("Status", back_populates="tickets")
    user = relationship("User", back_populates="tickets")
    
class Category(Base):
    __tablename__ = "ticket_categories"

    category_id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)

    # Add this to fix the error
    tickets = relationship("Ticket", back_populates="category")

