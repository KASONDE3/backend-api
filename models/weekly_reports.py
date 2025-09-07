from sqlalchemy import Column, Integer, String, Text, Date, DateTime, Boolean, Index
from sqlalchemy.sql import func
from db import Base

class WeeklyReportLog(Base):
    __tablename__ = "weekly_report_logs"

    id = Column(Integer, primary_key=True, index=True)
    report_date = Column(Date, index=True, nullable=False)  # The Monday date the report represents
    sent_at = Column(DateTime, server_default=func.now(), nullable=False)  # When it was actually sent
    recipients = Column(Text, nullable=False)  # Comma-separated list of recipient emails
    is_missed = Column(Boolean, default=False, nullable=False)  # True if sent after scheduled time
    report_payload = Column(Text, nullable=True)  # JSON string of the weekly report contents

    __table_args__ = (
        Index("idx_report_date_unique", "report_date", unique=True),
    )
