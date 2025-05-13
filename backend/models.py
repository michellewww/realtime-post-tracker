from sqlalchemy import Column, Integer, String, DateTime, Text,ForeignKey
from database import Base
from datetime import datetime
from zoneinfo import ZoneInfo
from sqlalchemy.orm import relationship

class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, index=True)
    topic = Column(String, index=True)
    interval_minutes = Column(Integer, default=1)
    last_sent = Column(DateTime, default=lambda: datetime.now(ZoneInfo("America/New_York")))
    sent_ids = Column(Text, default="")  # comma-separated tweet IDs
    tweets = relationship("Tweet", back_populates="subscription")
    

class Tweet(Base):
    __tablename__ = "tweets"

    id = Column(Integer, primary_key=True, index=True)
    tweet_id = Column(String, unique=True, index=True)
    topic = Column(String, index=True)
    content = Column(Text)
    author = Column(String)
    tweet_time = Column(DateTime)
    retrieved_at = Column(DateTime, default=lambda: datetime.now(ZoneInfo("America/New_York")))

    subscription_id = Column(Integer, ForeignKey("subscriptions.id"))
    subscription = relationship("Subscription", back_populates="tweets")

