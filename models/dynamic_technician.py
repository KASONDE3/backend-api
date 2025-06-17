# models.py

from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True)
    first_name = Column(String(255))
    last_name = Column(String(255))
    role = Column(String(50), nullable=False)

    # Relationship (not required for query but useful)
    assigned_tickets = relationship("Ticket", back_populates="technician", foreign_keys="Ticket.assigned_to")


class Ticket(Base):
    __tablename__ = "tickets"

    ticket_id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255))
    description = Column(Text)
    assigned_to = Column(Integer, ForeignKey("users.user_id"), nullable=True)

    technician = relationship("User", back_populates="assigned_tickets", foreign_keys=[assigned_to])
