"""
Main bot module for the Telegram moderation bot.
"""
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from app.config.settings import get_settings
from app.database.database import init_database, close_database
from app.handlers.messages import router
from app.logging.logger import setup_logging, get_logger
from app.middleware.logging import LoggingMiddleware

# Setup logging
setup_logging()
logger = get_logger(__name__)

async def main():
    """Main function to run the bot."""
    # Get settings
    settings = get_settings()
    
    # Validate bot token
    if not settings.bot.token:
        logger.error("BOT_TOKEN is not set in environment variables")
        return
    
    # Initialize database
    logger.info("Initializing database...")
    await init_database()
    logger.info("Database initialized successfully")
    
    # Create bot and dispatcher
    bot = Bot(
        token=settings.bot.token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()
    
    # Add middleware
    dp.message.middleware(LoggingMiddleware())
    
    # Include routers
    dp.include_router(router)
    
    # Start bot
    logger.info("Starting bot...")
    try:
        await dp.start_polling(bot)
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot error: {e}")
    finally:
        # Close database connections
        await close_database()
        await bot.session.close()
        logger.info("Bot stopped")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Program interrupted by user")
