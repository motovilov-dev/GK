from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv
from os import getenv

# Load environment variables from .env file
load_dotenv()


@dataclass
class Config:
    """Конфигурация бота"""
    # Токен бота
    token: str = getenv('BOT_TOKEN', '')
    dev_token: str = getenv('DEV_BOT_TOKEN', '')

    # Sentry
    sentry_dsn: str = getenv('SENTRY_DSN', '')
    sentry_dev_dsn: str = getenv('SENTRY_DEV_DSN', '')
    
    # Настройки webhook
    webhook_host: str = getenv('WEBHOOK_HOST', 'https://dev-bot.ru.tuna.am')
    webhook_path: str = getenv('WEBHOOK_PATH', '/webhook')
    webhook_port: str = getenv('WEBHOOK_PORT', '8080')

    # База данных (PostgreSQL)
    POSTGRES_SERVER: str = "195.133.27.192"
    POSTGRES_USER: str = "gen_user"
    POSTGRES_PASSWORD: str = "Alisa220!"
    POSTGRES_DB: str = "gk_bot"
    POSTGRES_PORT: int = 5432
    SQLALCHEMY_DATABASE_URI: str = f'postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}'
    
    # База URL для webhook
    webhook_base_url: Optional[str] = getenv('WEBHOOK_BASE_URL')

    # GK API
    GK_BASE_URL: str = 'https://api.goldenkey.world'
    
    @property
    def webhook_url(self) -> str:
        """Полный URL для webhook"""
        base_url = self.webhook_base_url or f'https://{self.webhook_host}'
        return f'{base_url}{self.webhook_path}'


config = Config()