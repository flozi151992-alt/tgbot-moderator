"""
Main entry point for the Telegram moderation bot.
"""
from app.bot.bot import main

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
