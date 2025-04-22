from sqlalchemy import Column, Integer, String, DateTime, Text
from database import Base
from datetime import datetime
from zoneinfo import ZoneInfo

class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, index=True)
    topic = Column(String, index=True)
    interval_minutes = Column(Integer, default=1)
    last_sent = Column(DateTime, default=lambda: datetime.now(ZoneInfo("America/New_York")))
    sent_ids = Column(Text, default="")  # comma-separated tweet IDs
