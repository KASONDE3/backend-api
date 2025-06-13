from sqlalchemy import Column, Integer, Enum
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class TicketCategory(Base):
    __tablename__ = "ticket_categories"
    category_id = Column(Integer, primary_key=True, index=True)
    name = Column(Enum('Computer Hardware', 'Computer Software', 'Network', 'Printer'), nullable=False)

class TicketPriority(Base):
    __tablename__ = "ticket_priorities"
    priority_id = Column(Integer, primary_key=True, index=True)
    name = Column(Enum('Low', 'Medium', 'High'), nullable=False)
    response_time = Column(Integer, nullable=False)

class Status(Base):
    __tablename__ = "statuses"
    status_id = Column(Integer, primary_key=True, index=True)
    name = Column(Enum('Open', 'In-progress', 'Completed'), nullable=False)
