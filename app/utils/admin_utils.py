"""
Utilities for admin permission checks and user management.
"""
from typing import List, Optional
from aiogram import Bot
from aiogram.types import ChatMember, ChatMemberAdministrator, ChatMemberOwner

from app.logging.logger import get_logger

logger = get_logger(__name__)

class AdminUtils:
    """Utilities for admin operations."""
    
    @staticmethod
    async def is_admin(bot: Bot, user_id: int, chat_id: int) -> bool:
        """Check if user is admin or owner of the chat."""
        try:
            member = await bot.get_chat_member(chat_id=chat_id, user_id=user_id)
            
            if isinstance(member, (ChatMemberAdministrator, ChatMemberOwner)):
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking admin status for user {user_id}: {e}")
            return False
    
    @staticmethod
    async def is_owner(bot: Bot, user_id: int, chat_id: int) -> bool:
        """Check if user is owner of the chat."""
        try:
            member = await bot.get_chat_member(chat_id=chat_id, user_id=user_id)
            return isinstance(member, ChatMemberOwner)
            
        except Exception as e:
            logger.error(f"Error checking owner status for user {user_id}: {e}")
            return False
    
    @staticmethod
    async def can_ban_users(bot: Bot, user_id: int, chat_id: int) -> bool:
        """Check if user can ban other users."""
        try:
            member = await bot.get_chat_member(chat_id=chat_id, user_id=user_id)
            
            if isinstance(member, ChatMemberOwner):
                return True
            
            if isinstance(member, ChatMemberAdministrator):
                return member.can_restrict_members
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking ban permissions for user {user_id}: {e}")
            return False
    
    @staticmethod
    async def get_chat_admins(bot: Bot, chat_id: int) -> List[dict]:
        """Get list of chat administrators."""
        try:
            admins = await bot.get_chat_administrators(chat_id=chat_id)
            
            admin_list = []
            for admin in admins:
                admin_info = {
                    'user_id': admin.user.id,
                    'username': admin.user.username,
                    'first_name': admin.user.first_name,
                    'last_name': admin.user.last_name,
                    'is_owner': isinstance(admin, ChatMemberOwner),
                    'can_restrict_members': getattr(admin, 'can_restrict_members', False) if isinstance(admin, ChatMemberAdministrator) else False
                }
                admin_list.append(admin_info)
            
            return admin_list
            
        except Exception as e:
            logger.error(f"Error getting chat admins: {e}")
            return []
    
    @staticmethod
    async def get_user_info(bot: Bot, user_id: int, chat_id: int) -> Optional[dict]:
        """Get user information from chat."""
        try:
            member = await bot.get_chat_member(chat_id=chat_id, user_id=user_id)
            
            return {
                'user_id': member.user.id,
                'username': member.user.username,
                'first_name': member.user.first_name,
                'last_name': member.user.last_name,
                'status': member.status,
                'is_admin': isinstance(member, (ChatMemberAdministrator, ChatMemberOwner)),
                'is_owner': isinstance(member, ChatMemberOwner)
            }
            
        except Exception as e:
            logger.error(f"Error getting user info for {user_id}: {e}")
            return None
