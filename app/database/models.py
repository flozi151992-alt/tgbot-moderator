"""
Database models for the Telegram bot.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, BigInteger, String, DateTime, Text
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class BotAction(Base):
    """Model for storing bot actions and logs."""
    __tablename__ = "bot_actions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=False, index=True)
    chat_id = Column(BigInteger, nullable=False, index=True)
    action_type = Column(String(50), nullable=False)  # 'message_received', 'message_deleted', 'error'
    message_text = Column(Text, nullable=True)
    reason = Column(String(200), nullable=True)  # Reason for deletion/action
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<BotAction(id={self.id}, user_id={self.user_id}, action_type='{self.action_type}')>"

class UserWarning(Base):
    """Model for storing user warnings and bans."""
    __tablename__ = "user_warnings"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=False, index=True)
    chat_id = Column(BigInteger, nullable=False, index=True)
    warning_count = Column(Integer, nullable=False, default=0)
    reason = Column(String(200), nullable=True)  # Reason for warning
    admin_id = Column(BigInteger, nullable=True)  # Admin who issued warning
    action_type = Column(String(50), nullable=False)  # 'warning', 'ban_24h', 'ban_permanent'
    ban_until = Column(DateTime(timezone=True), nullable=True)  # Ban expiration time
    is_active = Column(String(10), nullable=False, default='true')  # 'true' or 'false'
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<UserWarning(id={self.id}, user_id={self.user_id}, warning_count={self.warning_count}, action_type='{self.action_type}')>"
