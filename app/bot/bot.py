"""
Main bot module for the Telegram moderation bot.
"""
import asyncio
import os

from aiohttp import web
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
async def health(request):
    return web.Response(text="ok")


async def start_health_server():
    """Открывает порт, чтобы Render видел сервис как живой."""
    app = web.Application()
    app.router.add_get("/", health)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.getenv("PORT", "10000"))
    await web.TCPSite(runner, "0.0.0.0", port).start()
    logger.info(f"Health server started on port {port}")
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
    
    # Start health server for Render
    await start_health_server()
    
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
