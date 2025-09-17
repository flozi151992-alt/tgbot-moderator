"""
Configuration settings for the Telegram bot.
"""
import os
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

@dataclass
class DatabaseConfig:
    """Database configuration settings."""
    host: str
    port: int
    name: str
    user: str
    password: str
    
    @property
    def url(self) -> str:
        """Get database URL for SQLAlchemy."""
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"

@dataclass
class BotConfig:
    """Bot configuration settings."""
    token: str
    admin_id: int

@dataclass
class LoggingConfig:
    """Logging configuration settings."""
    level: str
    file_path: str

@dataclass
class Settings:
    """Main settings class."""
    bot: BotConfig
    database: DatabaseConfig
    logging: LoggingConfig

def get_settings() -> Settings:
    """Get application settings."""
    return Settings(
        bot=BotConfig(
            token=os.getenv("BOT_TOKEN", ""),
            admin_id=int(os.getenv("BOT_ADMIN_ID", "0"))
        ),
        database=DatabaseConfig(
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", "5432")),
            name=os.getenv("DB_NAME", "telegram_bot"),
            user=os.getenv("DB_USER", "bot_user"),
            password=os.getenv("DB_PASSWORD", "bot_password")
        ),
        logging=LoggingConfig(
            level=os.getenv("LOG_LEVEL", "INFO"),
            file_path=os.getenv("LOG_FILE_PATH", "logs/bot.log")
        )
    )
