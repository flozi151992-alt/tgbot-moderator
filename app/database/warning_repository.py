"""
Repository for user warnings and bans management.
"""
from typing import List, Optional
from datetime import datetime, timedelta
from sqlalchemy import select, desc, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.database import get_db_session, init_database
from app.database.models import UserWarning
from app.logging.logger import get_logger

logger = get_logger(__name__)

class WarningRepository:
    """Repository for managing user warnings and bans."""
    
    async def _ensure_database_initialized(self):
        """Ensure database is initialized before operations."""
        from app.database.database import async_session_maker
        if async_session_maker is None:
            await init_database()
    
    async def get_user_warnings(self, user_id: int, chat_id: int) -> Optional[UserWarning]:
        """Get current warning status for a user in a chat."""
        await self._ensure_database_initialized()
        async for session in get_db_session():
            stmt = (
                select(UserWarning)
                .where(
                    and_(
                        UserWarning.user_id == user_id,
                        UserWarning.chat_id == chat_id,
                        UserWarning.is_active == 'true'
                    )
                )
                .order_by(desc(UserWarning.timestamp))
                .limit(1)
            )
            result = await session.execute(stmt)
            return result.scalar_one_or_none()
    
    async def add_warning(self, user_id: int, chat_id: int, reason: str, admin_id: Optional[int] = None) -> UserWarning:
        """Add a warning to a user."""
        await self._ensure_database_initialized()
        async for session in get_db_session():
            # Get current warning status within the same session
            stmt = (
                select(UserWarning)
                .where(
                    and_(
                        UserWarning.user_id == user_id,
                        UserWarning.chat_id == chat_id,
                        UserWarning.is_active == 'true'
                    )
                )
                .order_by(desc(UserWarning.timestamp))
                .limit(1)
            )
            result = await session.execute(stmt)
            current_warning = result.scalar_one_or_none()
            
            if current_warning:
                # Update existing warning
                current_warning.warning_count += 1
                current_warning.reason = reason
                current_warning.admin_id = admin_id
                current_warning.timestamp = datetime.utcnow()
                
                # Determine action based on warning count
                if current_warning.warning_count >= 3:
                    # 3+ warnings = permanent ban
                    current_warning.action_type = 'ban_permanent'
                    current_warning.ban_until = None
                elif current_warning.warning_count >= 2:
                    # 2 warnings = 24h ban
                    current_warning.action_type = 'ban_24h'
                    current_warning.ban_until = datetime.utcnow() + timedelta(hours=24)
                else:
                    # 1 warning = just warning
                    current_warning.action_type = 'warning'
                    current_warning.ban_until = None
                
                await session.commit()
                return current_warning
            else:
                # Create new warning
                new_warning = UserWarning(
                    user_id=user_id,
                    chat_id=chat_id,
                    warning_count=1,
                    reason=reason,
                    admin_id=admin_id,
                    action_type='warning',
                    ban_until=None,
                    is_active='true'
                )
                session.add(new_warning)
                await session.commit()
                return new_warning
    
    async def is_user_banned(self, user_id: int, chat_id: int) -> bool:
        """Check if user is currently banned."""
        warning = await self.get_user_warnings(user_id, chat_id)
        if not warning:
            return False
        
        # Check if ban is still active
        if warning.action_type in ['ban_24h', 'ban_permanent']:
            if warning.action_type == 'ban_permanent':
                return True
            elif warning.ban_until:
                # Handle timezone comparison
                try:
                    current_time = datetime.utcnow()
                    if warning.ban_until.tzinfo is not None:
                        # warning.ban_until has timezone, make current_time timezone-aware
                        from datetime import timezone
                        current_time = current_time.replace(tzinfo=timezone.utc)
                    elif current_time.tzinfo is not None:
                        # current_time has timezone, make warning.ban_until timezone-aware
                        current_time = current_time.replace(tzinfo=None)
                    
                    if warning.ban_until > current_time:
                        return True
                    else:
                        # Ban expired, deactivate it
                        await self.deactivate_warning(warning.id)
                        return False
                except Exception as e:
                    # If comparison fails, assume ban is still active
                    logger.error(f"Error comparing ban times: {e}")
                    return True
        
        return False
    
    async def deactivate_warning(self, warning_id: int):
        """Deactivate a warning (used when ban expires)."""
        await self._ensure_database_initialized()
        async for session in get_db_session():
            stmt = select(UserWarning).where(UserWarning.id == warning_id)
            result = await session.execute(stmt)
            warning = result.scalar_one_or_none()
            
            if warning:
                warning.is_active = 'false'
                await session.commit()
    
    async def get_chat_warnings(self, chat_id: int, limit: int = 50) -> List[UserWarning]:
        """Get all active warnings for a chat."""
        await self._ensure_database_initialized()
        async for session in get_db_session():
            stmt = (
                select(UserWarning)
                .where(
                    and_(
                        UserWarning.chat_id == chat_id,
                        UserWarning.is_active == 'true'
                    )
                )
                .order_by(desc(UserWarning.timestamp))
                .limit(limit)
            )
            result = await session.execute(stmt)
            return result.scalars().all()
    
    async def clear_user_warnings(self, user_id: int, chat_id: int, admin_id: Optional[int] = None):
        """Clear all warnings for a user (admin action)."""
        await self._ensure_database_initialized()
        async for session in get_db_session():
            stmt = select(UserWarning).where(
                and_(
                    UserWarning.user_id == user_id,
                    UserWarning.chat_id == chat_id,
                    UserWarning.is_active == 'true'
                )
            )
            result = await session.execute(stmt)
            warnings = result.scalars().all()
            
            for warning in warnings:
                warning.is_active = 'false'
                warning.admin_id = admin_id
                warning.timestamp = datetime.utcnow()
            
            await session.commit()
    
    async def unban_user(self, user_id: int, chat_id: int, admin_id: Optional[int] = None) -> bool:
        """Unban a user by clearing all their warnings."""
        await self._ensure_database_initialized()
        async for session in get_db_session():
            # Get ALL warnings for user (both active and inactive)
            stmt = select(UserWarning).where(
                and_(
                    UserWarning.user_id == user_id,
                    UserWarning.chat_id == chat_id
                )
            )
            result = await session.execute(stmt)
            all_warnings = result.scalars().all()
            
            if not all_warnings:
                return False  # User has no warnings at all
            
            # Check if user has any active warnings
            active_warnings = [w for w in all_warnings if w.is_active == 'true']
            if not active_warnings:
                return False  # User not currently banned
            
            # Deactivate ALL warnings for this user
            for warning in all_warnings:
                warning.is_active = 'false'
                warning.admin_id = admin_id
                warning.timestamp = datetime.utcnow()
            
            await session.commit()
            return True
    
    async def get_user_warning_info(self, user_id: int, chat_id: int) -> Optional[dict]:
        """Get detailed warning information for a user."""
        warning = await self.get_user_warnings(user_id, chat_id)
        if not warning:
            return None
        
        return {
            'user_id': warning.user_id,
            'chat_id': warning.chat_id,
            'warning_count': warning.warning_count,
            'action_type': warning.action_type,
            'reason': warning.reason,
            'ban_until': warning.ban_until,
            'is_active': warning.is_active,
            'timestamp': warning.timestamp
        }
