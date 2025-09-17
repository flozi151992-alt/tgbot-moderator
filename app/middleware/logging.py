"""
Logging middleware for the Telegram bot.
"""
from aiogram import BaseMiddleware
from aiogram.types import Message
from typing import Callable, Dict, Any, Awaitable

from app.logging.logger import get_logger

logger = get_logger(__name__)

class LoggingMiddleware(BaseMiddleware):
    """Middleware for logging incoming messages."""
    
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        """Log message processing."""
        logger.info(f"Processing message from user {event.from_user.id} in chat {event.chat.id}")
        logger.info(f"Message type: {event.content_type}, text: {event.text[:50] if event.text else 'No text'}")
        
        return await handler(event, data)
