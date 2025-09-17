"""
Repository for database operations using SQLAlchemy ORM.
"""
from typing import List, Optional
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.database import get_db_session, init_database
from app.database.models import BotAction

class BotActionRepository:
    """Repository for bot actions using SQLAlchemy ORM."""
    
    async def _ensure_database_initialized(self):
        """Ensure database is initialized before operations."""
        from app.database.database import async_session_maker
        if async_session_maker is None:
            await init_database()
    
    async def create_action(
        self, 
        user_id: int, 
        chat_id: int, 
        action_type: str, 
        message_text: Optional[str] = None, 
        reason: Optional[str] = None
    ) -> int:
        """Create a new bot action record."""
        await self._ensure_database_initialized()
        async for session in get_db_session():
            action = BotAction(
                user_id=user_id,
                chat_id=chat_id,
                action_type=action_type,
                message_text=message_text,
                reason=reason
            )
            session.add(action)
            await session.commit()
            return action.id
    
    async def get_actions_by_chat(self, chat_id: int, limit: int = 100) -> List[dict]:
        """Get recent actions for a specific chat."""
        await self._ensure_database_initialized()
        async for session in get_db_session():
            stmt = (
                select(BotAction)
                .where(BotAction.chat_id == chat_id)
                .order_by(desc(BotAction.timestamp))
                .limit(limit)
            )
            result = await session.execute(stmt)
            actions = result.scalars().all()
            
            return [
                {
                    'id': action.id,
                    'user_id': action.user_id,
                    'chat_id': action.chat_id,
                    'action_type': action.action_type,
                    'message_text': action.message_text,
                    'reason': action.reason,
                    'timestamp': action.timestamp
                }
                for action in actions
            ]
    
    async def get_actions_by_user(self, user_id: int, limit: int = 100) -> List[dict]:
        """Get recent actions for a specific user."""
        await self._ensure_database_initialized()
        async for session in get_db_session():
            stmt = (
                select(BotAction)
                .where(BotAction.user_id == user_id)
                .order_by(desc(BotAction.timestamp))
                .limit(limit)
            )
            result = await session.execute(stmt)
            actions = result.scalars().all()
            
            return [
                {
                    'id': action.id,
                    'user_id': action.user_id,
                    'chat_id': action.chat_id,
                    'action_type': action.action_type,
                    'message_text': action.message_text,
                    'reason': action.reason,
                    'timestamp': action.timestamp
                }
                for action in actions
            ]
    
    async def get_all_actions(self, limit: int = 1000) -> List[dict]:
        """Get all recent actions."""
        await self._ensure_database_initialized()
        async for session in get_db_session():
            stmt = (
                select(BotAction)
                .order_by(desc(BotAction.timestamp))
                .limit(limit)
            )
            result = await session.execute(stmt)
            actions = result.scalars().all()
            
            return [
                {
                    'id': action.id,
                    'user_id': action.user_id,
                    'chat_id': action.chat_id,
                    'action_type': action.action_type,
                    'message_text': action.message_text,
                    'reason': action.reason,
                    'timestamp': action.timestamp
                }
                for action in actions
            ]