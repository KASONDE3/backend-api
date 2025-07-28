from sqlalchemy import Column, Integer, Text, ForeignKey, TIMESTAMP, func
from db import Base

class Recommendation(Base):
    __tablename__ = 'recommendations'

    recomm_id = Column(Integer, primary_key=True, autoincrement=True)
    ticket_id = Column(Integer, ForeignKey('tickets.ticket_id'), nullable=False)
    recommendation = Column(Text, nullable=False)
    created_by = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.current_timestamp()) 