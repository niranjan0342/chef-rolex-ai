from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, ForeignKey
from sqlalchemy.sql import func
from app.db.session import Base

# Table 1 — Users
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(150), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())


# Table 2 — Sessions
class ChatSession(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), unique=True, nullable=False)
    title = Column(String(200), default="New Chat")
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(TIMESTAMP, server_default=func.now())


# Table 3 — Messages
class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), ForeignKey("sessions.session_id"))
    role = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())