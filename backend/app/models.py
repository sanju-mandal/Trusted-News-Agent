# backend/app/models.py
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String(255), unique=True, index=True, nullable=True)
    name = Column(String(255), nullable=True)

    interactions = relationship("NewsInteraction", back_populates="user")

class NewsInteraction(Base):
    __tablename__ = "news_interactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    type = Column(String(50))  # "search" | "user_input"
    topic = Column(String(255), nullable=True)
    title = Column(String(512), nullable=True)
    url = Column(String(512), nullable=True)
    raw_text = Column(Text, nullable=True)

    label = Column(String(20))         # "real" | "fake" | "uncertain"
    confidence = Column(Float)
    summary = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="interactions")
