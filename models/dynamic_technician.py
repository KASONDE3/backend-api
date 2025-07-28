# models.py

from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from models.ticketModels import User, Ticket


class DynamicTechnician:
    def __init__(self, user_id: int):
        self.user_id = user_id
        self.user = User.query.get(user_id)
        self.tickets = Ticket.query.filter_by(assigned_to=user_id).all()

    def get_assigned_tickets(self):
        return self.tickets

    def get_user_info(self):
        return {
            "user_id": self.user.user_id,
            "email": self.user.email,
            "first_name": self.user.first_name,
            "last_name": self.user.last_name,
            "role": self.user.role
        }
