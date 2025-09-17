"""
Utilities for handling user bans and restrictions.
"""
from datetime import datetime, timedelta
from typing import Optional
from aiogram import Bot
from aiogram.types import ChatPermissions

from app.database.warning_repository import WarningRepository
from app.logging.logger import get_logger

logger = get_logger(__name__)

class BanManager:
    """Manager for handling user bans and restrictions."""
    
    def __init__(self):
        self.warning_repo = WarningRepository()
    
    async def handle_profanity_violation(self, bot: Bot, user_id: int, chat_id: int, message_text: str) -> bool:
        """
        Handle profanity violation - add warning and apply appropriate punishment.
        Returns True if user was banned, False otherwise.
        """
        try:
            # Add warning
            warning = await self.warning_repo.add_warning(
                user_id=user_id,
                chat_id=chat_id,
                reason=f"Profanity: {message_text[:50]}"
            )
            
            logger.info(f"Warning added for user {user_id} in chat {chat_id}. Count: {warning.warning_count}")
            
            # Apply punishment based on warning count
            if warning.warning_count == 1:
                # First warning - just send message
                await self._send_warning_message(bot, chat_id, user_id, warning.warning_count)
                return False
                
            elif warning.warning_count == 2:
                # Second warning - 24h ban
                await self._ban_user_24h(bot, chat_id, user_id)
                await self._send_ban_message(bot, chat_id, user_id, "24 часа", warning.warning_count)
                return True
                
            elif warning.warning_count >= 3:
                # Third+ warning - permanent ban
                await self._ban_user_permanent(bot, chat_id, user_id)
                await self._send_ban_message(bot, chat_id, user_id, "навсегда", warning.warning_count)
                return True
                
        except Exception as e:
            logger.error(f"Error handling profanity violation: {e}")
            return False
    
    async def _send_warning_message(self, bot: Bot, chat_id: int, user_id: int, warning_count: int):
        """Send warning message to user."""
        try:
            username = f"@{user_id}"  # We'll get actual username from message context
            message_text = (
                f"⚠️ {username}, вы получили предупреждение за нарушение правил чата.\n"
                f"Количество предупреждений: {warning_count}/3\n\n"
                f"При следующем нарушении вы будете заблокированы на 24 часа."
            )
            
            await bot.send_message(chat_id=chat_id, text=message_text)
            logger.info(f"Warning message sent to user {user_id} in chat {chat_id}")
            
        except Exception as e:
            logger.error(f"Error sending warning message: {e}")
    
    async def _send_ban_message(self, bot: Bot, chat_id: int, user_id: int, ban_duration: str, warning_count: int):
        """Send ban notification message."""
        try:
            username = f"@{user_id}"  # We'll get actual username from message context
            message_text = (
                f"🚫 {username} заблокирован {ban_duration} за нарушение правил чата.\n"
                f"Количество предупреждений: {warning_count}/3\n\n"
                f"Соблюдайте правила чата для комфортного общения всех участников."
            )
            
            await bot.send_message(chat_id=chat_id, text=message_text)
            logger.info(f"Ban message sent for user {user_id} in chat {chat_id}")
            
        except Exception as e:
            logger.error(f"Error sending ban message: {e}")
    
    async def _ban_user_24h(self, bot: Bot, chat_id: int, user_id: int):
        """Ban user for 24 hours."""
        try:
            # Restrict user permissions for 24 hours
            until_date = int((datetime.utcnow() + timedelta(hours=24)).timestamp())
            
            await bot.restrict_chat_member(
                chat_id=chat_id,
                user_id=user_id,
                permissions=ChatPermissions(can_send_messages=False),
                until_date=until_date
            )
            
            logger.info(f"User {user_id} banned for 24h in chat {chat_id}")
            
        except Exception as e:
            logger.error(f"Error banning user for 24h: {e}")
    
    async def _ban_user_permanent(self, bot: Bot, chat_id: int, user_id: int):
        """Permanently ban user."""
        try:
            await bot.ban_chat_member(chat_id=chat_id, user_id=user_id)
            logger.info(f"User {user_id} permanently banned in chat {chat_id}")
            
        except Exception as e:
            logger.error(f"Error permanently banning user: {e}")
    
    async def check_user_ban_status(self, user_id: int, chat_id: int) -> bool:
        """Check if user is currently banned."""
        return await self.warning_repo.is_user_banned(user_id, chat_id)
    
    async def get_user_warning_count(self, user_id: int, chat_id: int) -> int:
        """Get current warning count for user."""
        warning = await self.warning_repo.get_user_warnings(user_id, chat_id)
        return warning.warning_count if warning else 0
    
    async def unban_user(self, bot: Bot, user_id: int, chat_id: int, admin_id: int) -> bool:
        """
        Unban a user - remove all warnings and restore permissions.
        Returns True if user was unbanned, False if user wasn't banned.
        """
        try:
            # Check if user is actually banned
            is_banned = await self.check_user_ban_status(user_id, chat_id)
            if not is_banned:
                return False
            
            # Get warning info before unbanning
            warning_info = await self.warning_repo.get_user_warning_info(user_id, chat_id)
            
            # Unban user in database
            success = await self.warning_repo.unban_user(user_id, chat_id, admin_id)
            if not success:
                return False
            
            # Restore user permissions in Telegram
            try:
                await bot.unban_chat_member(chat_id=chat_id, user_id=user_id)
                logger.info(f"User {user_id} unbanned from chat {chat_id} by admin {admin_id}")
            except Exception as e:
                logger.warning(f"Failed to unban user {user_id} in Telegram: {e}")
                # Continue anyway, database unban is more important
            
            # Send unban notification
            try:
                if warning_info:
                    message_text = (
                        f"✅ Пользователь разбанен администратором.\n"
                        f"Предыдущие предупреждения: {warning_info['warning_count']}/3\n"
                        f"Причина последнего нарушения: {warning_info['reason']}\n\n"
                        f"Пожалуйста, соблюдайте правила чата."
                    )
                else:
                    message_text = "✅ Пользователь разбанен администратором."
                
                await bot.send_message(chat_id=chat_id, text=message_text)
                logger.info(f"Unban notification sent for user {user_id} in chat {chat_id}")
                
            except Exception as e:
                logger.error(f"Failed to send unban notification: {e}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error unbanning user {user_id}: {e}")
            return False
    
    async def get_user_warning_info(self, user_id: int, chat_id: int) -> Optional[dict]:
        """Get detailed warning information for a user."""
        return await self.warning_repo.get_user_warning_info(user_id, chat_id)
