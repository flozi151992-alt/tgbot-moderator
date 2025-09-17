"""
Message handlers for the Telegram bot.
"""
from aiogram import Router, types, Bot
from aiogram.filters import Command
from aiogram.types import Message

from app.database.repository import BotActionRepository
from app.filters.profanity import profanity_filter
from app.logging.logger import get_logger
from app.utils.ban_utils import BanManager
from app.utils.admin_utils import AdminUtils

logger = get_logger(__name__)
router = Router()
ban_manager = BanManager()

@router.errors()
async def error_handler(event: types.ErrorEvent):
    """Handle errors in message processing."""
    logger.error(f"Error occurred: {event.exception}")
    
    # Log error to database
    try:
        repo = BotActionRepository()
        await repo.create_action(
            user_id=0,  # System error
            chat_id=0,
            action_type="error",
            message_text=str(event.exception),
            reason="system_error"
        )
    except Exception as log_error:
        logger.error(f"Failed to log error: {log_error}")

def get_chat_rules():
    """Generate chat rules message."""
    return (
        "📋 **Правила чата**\n\n"
        "🚫 **Запрещено:**\n"
        "• Использование нецензурной лексики\n"
        "• Спам и реклама\n"
        "• Оскорбления участников\n"
        "• Распространение запрещенного контента\n\n"
        "✅ **Разрешено:**\n"
        "• Вежливое общение\n"
        "• Обсуждение по теме чата\n"
        "• Конструктивная критика\n"
        "• Помощь другим участникам\n\n"
        "⚠️ **Система предупреждений:**\n"
        "• 1-е нарушение: предупреждение\n"
        "• 2-е нарушение: блокировка на 24 часа\n"
        "• 3-е нарушение: постоянная блокировка\n\n"
        "🔧 Модерация осуществляется автоматически. Нарушения фиксируются в логах.\n\n"
        "⚠️ При нарушении правил сообщение будет удалено автоматически."
    )

@router.message(Command("start"))
async def cmd_start(message: types.Message):
    """Handle /start command."""
    if message.chat.type == 'private':
        await message.reply(
            "👋 Привет! Я бот-модератор.\n\n"
            "Я помогаю поддерживать порядок в чате, удаляя сообщения с нецензурной лексикой.\n"
            "Просто добавьте меня в ваш чат и дайте права администратора для удаления сообщений.\n\n"
            "⚠️ **Система предупреждений:**\n"
            "• 1-е нарушение: предупреждение\n"
            "• 2-е нарушение: блокировка на 24 часа\n"
            "• 3-е нарушение: постоянная блокировка"
        )
    else:
        await message.reply(
            "👋 Бот-модератор активирован!\n\n"
            "Я буду автоматически удалять сообщения с нецензурной лексикой в этом чате.\n"
            "Используйте /help для просмотра команд.\n\n"
            f"{get_chat_rules()}"
        )
    
    # Log the start command
    repo = BotActionRepository()
    await repo.create_action(
        user_id=message.from_user.id,
        chat_id=message.chat.id,
        action_type="start_command",
        message_text="/start"
    )
    
    logger.info(f"Start command from user {message.from_user.id} in chat {message.chat.id}")

@router.message(Command("help"))
async def cmd_help(message: types.Message):
    """Handle /help command."""
    if message.chat.type == 'private':
        await message.reply(
            "🤖 Команды бота-модератора:\n\n"
            "/start - Запустить бота\n"
            "/help - Показать эту справку\n"
            "/rules - Показать правила чата\n"
            "/stats - Статистика модерации (только для админов)\n\n"
            "Бот автоматически удаляет сообщения с нецензурной лексикой."
        )
    else:
        await message.reply(
            "🤖 **Команды бота-модератора:**\n\n"
            "📋 `/rules` - Показать правила чата\n"
            "📊 `/stats` - Статистика модерации\n"
            "❓ `/help` - Показать это сообщение\n\n"
            "👮 **Команды для администраторов:**\n"
            "🔓 `/unban [user_id]` - Разбанить пользователя\n"
            "📋 `/warnings [user_id]` - Показать предупреждения пользователя\n"
            "📊 `/status [user_id]` - Проверить статус пользователя\n"
            "🔍 `/search [partial_id]` - Найти пользователей по части ID\n"
            "👥 `/admins` - Список администраторов\n\n"
            "🔧 Бот автоматически удаляет сообщения с нецензурной лексикой."
        )
    
    # Log the help command
    repo = BotActionRepository()
    await repo.create_action(
        user_id=message.from_user.id,
        chat_id=message.chat.id,
        action_type="help_command",
        message_text="/help"
    )

@router.message(Command("rules"))
async def cmd_rules(message: types.Message):
    """Handle /rules command - show chat rules."""
    await message.reply(get_chat_rules())
    
    # Log the rules command
    repo = BotActionRepository()
    await repo.create_action(
        user_id=message.from_user.id,
        chat_id=message.chat.id,
        action_type="rules_command",
        message_text="/rules"
    )
    
    logger.info(f"Rules command from user {message.from_user.id} in chat {message.chat.id}")

@router.message(Command("stats"))
async def cmd_stats(message: types.Message):
    """Handle /stats command - show moderation statistics."""
    # Only work in groups/supergroups
    if message.chat.type not in ['group', 'supergroup']:
        await message.reply("❌ Эта команда работает только в группах.")
        return
    
    try:
        # Get chat administrators
        chat_admins = await message.bot.get_chat_administrators(message.chat.id)
        admin_ids = [admin.user.id for admin in chat_admins]
        
        # Check if user is admin
        if message.from_user.id not in admin_ids:
            await message.reply("❌ Эта команда доступна только администраторам чата.")
            return
        
        # Get statistics from database
        repo = BotActionRepository()
        recent_actions = await repo.get_actions_by_chat(message.chat.id, limit=100)
        
        deleted_messages = len([a for a in recent_actions if a['action_type'] == "message_deleted"])
        total_messages = len([a for a in recent_actions if a['action_type'] == "message_received"])
        
        stats_text = (
            f"📊 Статистика модерации для этого чата:\n\n"
            f"📝 Всего сообщений: {total_messages}\n"
            f"🗑 Удалено сообщений: {deleted_messages}\n"
            f"📈 Процент удаленных: {(deleted_messages/total_messages*100):.1f}%"
            if total_messages > 0 else "📊 Пока нет статистики для этого чата."
        )
        
        await message.reply(stats_text)
    
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        await message.reply("❌ Ошибка получения статистики.")

async def handle_text_message(message: types.Message, bot: Bot):
    """Handle text messages and check for profanity."""
    # DEBUG: Log all incoming messages
    logger.info(f"DEBUG: Received message from user {message.from_user.id} in chat {message.chat.id} (type: {message.chat.type})")
    logger.info(f"DEBUG: Message text: {message.text[:100] if message.text else 'No text'}")
    logger.info(f"DEBUG: Chat title: {getattr(message.chat, 'title', 'No title')}")
    logger.info(f"DEBUG: User name: {message.from_user.first_name} {message.from_user.last_name or ''}")
    logger.info(f"DEBUG: Message ID: {message.message_id}")
    logger.info(f"DEBUG: Chat username: {getattr(message.chat, 'username', 'No username')}")
    
    try:
        # Check if user is banned
        is_banned = await ban_manager.check_user_ban_status(message.from_user.id, message.chat.id)
        if is_banned:
            logger.info(f"User {message.from_user.id} is banned, ignoring message")
            return
        
        # Log incoming message
        repo = BotActionRepository()
        await repo.create_action(
            user_id=message.from_user.id,
            chat_id=message.chat.id,
            action_type="message_received",
            message_text=message.text[:500]  # Limit text length
        )
        
        # Check for profanity
        if profanity_filter.contains_profanity(message.text):
            # Delete the message first
            try:
                await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
                logger.info(f"Message deleted successfully from user {message.from_user.id} in chat {message.chat.id}")
            except Exception as e:
                logger.error(f"Failed to delete message: {e}")
                return  # Exit if we can't delete the message
            
            # Get detected words for logging
            detected_words = profanity_filter.get_detected_words(message.text)
            reason = f"Profanity detected: {', '.join(detected_words[:3])}"  # Limit to first 3 words
            
            # Log the deletion
            try:
                repo = BotActionRepository()
                await repo.create_action(
                    user_id=message.from_user.id,
                    chat_id=message.chat.id,
                    action_type="message_deleted",
                    message_text=message.text[:500],
                    reason=reason
                )
                logger.info(f"Logged deletion for user {message.from_user.id} in chat {message.chat.id}. Reason: {reason}")
            except Exception as e:
                logger.error(f"Failed to log deletion: {e}")
            
            # Handle profanity violation with warning system
            try:
                user_banned = await ban_manager.handle_profanity_violation(
                    bot=bot,
                    user_id=message.from_user.id,
                    chat_id=message.chat.id,
                    message_text=message.text
                )
                
                if user_banned:
                    logger.info(f"User {message.from_user.id} was banned for profanity violation")
                else:
                    logger.info(f"Warning issued to user {message.from_user.id} for profanity violation")
                    
            except Exception as ban_error:
                logger.error(f"Failed to handle profanity violation: {ban_error}")
                
                # Fallback to old warning message
                try:
                    username = f"@{message.from_user.username}" if message.from_user.username else message.from_user.first_name
                    warning_text = f"⚠️ {username}, ваше сообщение было удалено. Причина: нецензурная лексика."
                    
                    warning_message = await bot.send_message(
                        chat_id=message.chat.id,
                        text=warning_text
                    )
                    
                    # Delete warning after 30 seconds
                    import asyncio
                    await asyncio.sleep(30)
                    try:
                        await bot.delete_message(chat_id=message.chat.id, message_id=warning_message.message_id)
                    except Exception:
                        pass
                        
                except Exception as warning_error:
                    logger.error(f"Failed to send fallback warning message: {warning_error}")
    
    except Exception as e:
        logger.error(f"Error handling message: {e}")

@router.message(Command("unban"))
async def cmd_unban(message: types.Message, bot: Bot):
    """Handle /unban command - unban a user."""
    if message.chat.type == 'private':
        await message.reply("❌ Эта команда работает только в групповых чатах.")
        return
    
    # Check if user is admin
    is_admin = await AdminUtils.is_admin(bot, message.from_user.id, message.chat.id)
    if not is_admin:
        await message.reply("❌ У вас нет прав для выполнения этой команды.")
        return
    
    # Parse command arguments
    args = message.text.split()
    if len(args) < 2:
        await message.reply("❌ Использование: `/unban [user_id]`\nПример: `/unban 123456789`")
        return
    
    try:
        user_id = int(args[1])
    except ValueError:
        await message.reply("❌ Неверный формат user_id. Используйте только цифры.")
        return
    
    # Check if user is banned in bot system
    is_banned_in_bot = await ban_manager.check_user_ban_status(user_id, message.chat.id)
    
    # Try to unban/unrestrict user in Telegram
    telegram_unban_success = False
    user_status = "unknown"
    try:
        # First, try to get user status to determine the best approach
        try:
            member = await bot.get_chat_member(chat_id=message.chat.id, user_id=user_id)
            user_status = member.status
        except Exception:
            user_status = "unknown"
        
        if user_status == "restricted":
            # User is restricted, restore full permissions
            from aiogram.types import ChatPermissions
            await bot.restrict_chat_member(
                chat_id=message.chat.id,
                user_id=user_id,
                permissions=ChatPermissions(
                    can_send_messages=True,
                    can_send_media_messages=True,
                    can_send_polls=True,
                    can_send_other_messages=True,
                    can_add_web_page_previews=True,
                    can_change_info=False,
                    can_invite_users=False,
                    can_pin_messages=False
                )
            )
            telegram_unban_success = True
            logger.info(f"User {user_id} unrestricted in Telegram by admin {message.from_user.id}")
        elif user_status in ["kicked", "left"]:
            # User was banned/kicked, use unban_chat_member
            await bot.unban_chat_member(chat_id=message.chat.id, user_id=user_id)
            telegram_unban_success = True
            logger.info(f"User {user_id} unbanned from Telegram by admin {message.from_user.id}")
        else:
            # Try unban anyway
            await bot.unban_chat_member(chat_id=message.chat.id, user_id=user_id)
            telegram_unban_success = True
            logger.info(f"User {user_id} unbanned from Telegram by admin {message.from_user.id}")
            
    except Exception as e:
        telegram_unban_success = False
        logger.warning(f"Failed to unban user {user_id} in Telegram: {e}")
    
    # If user was banned in bot system, clear warnings
    bot_unban_success = False
    if is_banned_in_bot:
        bot_unban_success = await ban_manager.unban_user(bot, user_id, message.chat.id, message.from_user.id)
    
    # Prepare result message
    if telegram_unban_success or bot_unban_success:
        result_parts = []
        if telegram_unban_success:
            if user_status == "restricted":
                result_parts.append("✅ Сняты ограничения в Telegram")
            else:
                result_parts.append("✅ Разбанен в Telegram")
        if bot_unban_success:
            result_parts.append("✅ Очищены предупреждения бота")
        if not is_banned_in_bot and telegram_unban_success:
            if user_status == "restricted":
                result_parts.append("(пользователь был ограничен)")
            else:
                result_parts.append("(пользователь был забанен вручную)")
            
        result_message = f"✅ Пользователь {user_id} успешно разбанен.\n" + "\n".join(result_parts)
        await message.reply(result_message)
        
        # Log the unban action
        repo = BotActionRepository()
        await repo.create_action(
            user_id=message.from_user.id,
            chat_id=message.chat.id,
            action_type="admin_unban",
            message_text=f"Unbanned user {user_id} (Telegram: {telegram_unban_success}, Bot: {bot_unban_success})",
            reason="admin_action"
        )
    else:
        await message.reply(f"❌ Не удалось разбанить пользователя {user_id}. Возможно, пользователь не забанен или произошла ошибка.")

@router.message(Command("warnings"))
async def cmd_warnings(message: types.Message, bot: Bot):
    """Handle /warnings command - show user warnings."""
    if message.chat.type == 'private':
        await message.reply("❌ Эта команда работает только в групповых чатах.")
        return
    
    # Check if user is admin
    is_admin = await AdminUtils.is_admin(bot, message.from_user.id, message.chat.id)
    if not is_admin:
        await message.reply("❌ У вас нет прав для выполнения этой команды.")
        return
    
    # Parse command arguments
    args = message.text.split()
    if len(args) < 2:
        await message.reply("❌ Использование: `/warnings [user_id]`\nПример: `/warnings 123456789`")
        return
    
    try:
        user_id = int(args[1])
    except ValueError:
        await message.reply("❌ Неверный формат user_id. Используйте только цифры.")
        return
    
    # Get user warning info
    warning_info = await ban_manager.get_user_warning_info(user_id, message.chat.id)
    if not warning_info:
        await message.reply(f"ℹ️ У пользователя {user_id} нет предупреждений.")
        return
    
    # Format warning info
    warning_text = (
        f"📋 **Предупреждения пользователя {user_id}:**\n\n"
        f"⚠️ Количество предупреждений: {warning_info['warning_count']}/3\n"
        f"🚫 Статус: {warning_info['action_type']}\n"
        f"📝 Причина: {warning_info['reason']}\n"
        f"🕐 Время: {warning_info['timestamp'].strftime('%d.%m.%Y %H:%M')}\n"
    )
    
    if warning_info['ban_until']:
        warning_text += f"⏰ Бан до: {warning_info['ban_until'].strftime('%d.%m.%Y %H:%M')}\n"
    
    await message.reply(warning_text)

@router.message(Command("admins"))
async def cmd_admins(message: types.Message, bot: Bot):
    """Handle /admins command - show chat administrators."""
    if message.chat.type == 'private':
        await message.reply("❌ Эта команда работает только в групповых чатах.")
        return
    
    # Get chat admins
    admins = await AdminUtils.get_chat_admins(bot, message.chat.id)
    if not admins:
        await message.reply("❌ Не удалось получить список администраторов.")
        return
    
    # Format admin list
    admin_text = "👥 **Администраторы чата:**\n\n"
    for admin in admins:
        name = admin['first_name']
        if admin['last_name']:
            name += f" {admin['last_name']}"
        
        username = f"@{admin['username']}" if admin['username'] else "Нет username"
        role = "👑 Владелец" if admin['is_owner'] else "👮 Администратор"
        
        admin_text += f"{role}: {name} ({username})\n"
        admin_text += f"   ID: {admin['user_id']}\n\n"
    
    await message.reply(admin_text)

@router.message(Command("status"))
async def cmd_status(message: types.Message, bot: Bot):
    """Handle /status command - check user status in chat."""
    if message.chat.type == 'private':
        await message.reply("❌ Эта команда работает только в групповых чатах.")
        return
    
    # Check if user is admin
    is_admin = await AdminUtils.is_admin(bot, message.from_user.id, message.chat.id)
    if not is_admin:
        await message.reply("❌ У вас нет прав для выполнения этой команды.")
        return
    
    # Parse command arguments
    args = message.text.split()
    if len(args) < 2:
        await message.reply("❌ Использование: `/status [user_id]`\nПример: `/status 123456789`")
        return
    
    try:
        user_id = int(args[1])
    except ValueError:
        await message.reply("❌ Неверный формат user_id. Используйте только цифры.")
        return
    
    try:
        # Get user status in bot system first
        is_banned_in_bot = await ban_manager.check_user_ban_status(user_id, message.chat.id)
        warning_info = await ban_manager.get_user_warning_info(user_id, message.chat.id)
        
        # Try to get user status in Telegram
        telegram_status = "Неизвестно"
        user_info = None
        try:
            member = await bot.get_chat_member(chat_id=message.chat.id, user_id=user_id)
            telegram_status = member.status
            user_info = member.user
            until_date = getattr(member, 'until_date', None)
        except Exception as telegram_error:
            if "PARTICIPANT_ID_INVALID" in str(telegram_error):
                telegram_status = "Не найден в чате (возможно, покинул или был удален)"
            else:
                telegram_status = f"Ошибка: {telegram_error}"
        
        # Format status message
        status_text = f"📊 **Статус пользователя {user_id}:**\n\n"
        
        # Telegram status
        status_text += f"🔹 **Telegram статус:** {telegram_status}\n"
        if 'until_date' in locals() and until_date:
            status_text += f"   Ограничен до: {until_date.strftime('%d.%m.%Y %H:%M')}\n"
        
        # Bot system status
        status_text += f"🔹 **Статус в боте:** {'Забанен' if is_banned_in_bot else 'Не забанен'}\n"
        
        if warning_info:
            status_text += f"🔹 **Предупреждения:** {warning_info['warning_count']}/3\n"
            status_text += f"🔹 **Тип действия:** {warning_info['action_type']}\n"
            status_text += f"🔹 **Причина:** {warning_info['reason']}\n"
            try:
                timestamp = warning_info['timestamp']
                if hasattr(timestamp, 'strftime'):
                    status_text += f"🔹 **Время:** {timestamp.strftime('%d.%m.%Y %H:%M')}\n"
                else:
                    status_text += f"🔹 **Время:** {str(timestamp)}\n"
            except Exception:
                status_text += f"🔹 **Время:** Неизвестно\n"
        else:
            status_text += f"🔹 **Предупреждения:** Нет\n"
        
        # User info
        if user_info:
            name = user_info.first_name
            if user_info.last_name:
                name += f" {user_info.last_name}"
            username = f"@{user_info.username}" if user_info.username else "Нет username"
            status_text += f"\n👤 **Пользователь:** {name} ({username})\n"
        
        await message.reply(status_text)
        
    except Exception as e:
        logger.error(f"Error checking user status: {e}")
        await message.reply(f"❌ Ошибка при проверке статуса пользователя {user_id}: {e}")

@router.message(Command("search"))
async def cmd_search(message: types.Message, bot: Bot):
    """Handle /search command - search for users with similar IDs."""
    if message.chat.type == 'private':
        await message.reply("❌ Эта команда работает только в групповых чатах.")
        return
    
    # Check if user is admin
    is_admin = await AdminUtils.is_admin(bot, message.from_user.id, message.chat.id)
    if not is_admin:
        await message.reply("❌ У вас нет прав для выполнения этой команды.")
        return
    
    # Parse command arguments
    args = message.text.split()
    if len(args) < 2:
        await message.reply("❌ Использование: `/search [partial_user_id]`\nПример: `/search 694265`")
        return
    
    search_term = args[1]
    
    try:
        from app.database.database import get_db_session
        from sqlalchemy import select, desc, or_, cast, String
        from app.database.models import UserWarning
        
        async for session in get_db_session():
            # Search for users with similar IDs
            stmt = (
                select(UserWarning)
                .where(cast(UserWarning.user_id, String).like(f'%{search_term}%'))
                .order_by(desc(UserWarning.timestamp))
                .limit(10)
            )
            result = await session.execute(stmt)
            warnings = result.scalars().all()
            
            if warnings:
                search_text = f"🔍 **Найденные пользователи (поиск: {search_term}):**\n\n"
                
                seen_users = set()
                for warning in warnings:
                    if warning.user_id not in seen_users:
                        seen_users.add(warning.user_id)
                        search_text += f"👤 **User ID:** {warning.user_id}\n"
                        search_text += f"   Предупреждений: {warning.warning_count}/3\n"
                        search_text += f"   Статус: {warning.action_type}\n"
                        search_text += f"   Активен: {warning.is_active}\n"
                        search_text += f"   Последняя причина: {warning.reason}\n"
                        try:
                            if hasattr(warning.timestamp, 'strftime'):
                                search_text += f"   Время: {warning.timestamp.strftime('%d.%m.%Y %H:%M')}\n\n"
                            else:
                                search_text += f"   Время: {str(warning.timestamp)}\n\n"
                        except Exception:
                            search_text += f"   Время: Неизвестно\n\n"
                
                await message.reply(search_text)
            else:
                await message.reply(f"❌ Пользователи с ID, содержащим '{search_term}', не найдены.")
            
            break
            
    except Exception as e:
        logger.error(f"Error searching users: {e}")
        await message.reply(f"❌ Ошибка поиска: {e}")

@router.message()
async def handle_message(message: types.Message, bot: Bot):
    """Handle all messages."""
    # Skip messages from bots
    if message.from_user.is_bot:
        logger.info("DEBUG: Skipping message from bot")
        return
    
    # Only moderate in groups and supergroups (not in private chats)
    if message.chat.type == 'private':
        logger.info("DEBUG: Skipping private chat message")
        return
    
    # Handle text messages
    if message.content_type == "text":
        await handle_text_message(message, bot)
    else:
        logger.info(f"DEBUG: Non-text message ignored: {message.content_type}")

