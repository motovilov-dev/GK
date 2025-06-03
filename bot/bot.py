import asyncio
import logging
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration, SentryLogsHandler

from config import config
from loguru import logger as loguru_logger
from sentry_sdk import logger as sentry_logger
from dotenv import load_dotenv
from middleware import ThrottlingMiddleware, LoggingMiddleware
from routers import main_router, user_router
from aiogram.fsm.storage.memory import MemoryStorage

loguru_logger.add(
    "bot.log",
    rotation="100 MB",
    retention="100 days",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
)

sentry_sdk.init(
    dsn=config.sentry_dev_dsn,
    send_default_pii=True,
    traces_sample_rate=1.0,
    profiles_sample_rate=1.0,
    _experiments={
        "enable_logs": True,
    },
    integrations=[LoggingIntegration(sentry_logs_level=None)],
)

# Инициализация бота и диспетчера
storage = MemoryStorage()
bot = Bot(token=config.token, default=DefaultBotProperties(parse_mode='HTML'))
dp = Dispatcher(storage=storage)

# Подключение middleware
dp.update.outer_middleware(LoggingMiddleware())
dp.message.middleware(ThrottlingMiddleware())

# Подключение роутеров
dp.include_router(main_router)
# dp.include_router(admin_router)
dp.include_router(user_router)


async def on_startup(bot: Bot) -> None:
    """Действия при запуске бота"""
    # Установка webhook
    await bot.set_webhook(
        url=config.webhook_url,
        drop_pending_updates=True
    )
    sentry_logger.info(f'Webhook установлен на {config.webhook_url}')


async def on_shutdown(bot: Bot) -> None:
    """Действия при остановке бота"""
    # Удаление webhook
    await bot.delete_webhook()
    sentry_logger.trace('Webhook удаляется')
    sentry_logger.info('Webhook удален')


async def start_bot_webhook() -> None:
    """Запуск бота в режиме webhook"""
    # Создание приложения aiohttp
    app = web.Application()
    
    # Настройка webhook handler
    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot
    )
    webhook_requests_handler.register(app, path=config.webhook_path)
    
    # Настройка startup и shutdown
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    
    # Настройка aiohttp приложения
    setup_application(app, dp, bot=bot)
    
    # Запуск веб-сервера
    sentry_logger.info("Запуск веб сервера")
    
    await bot.set_webhook(
        url=config.webhook_url,
        drop_pending_updates=True,
        allowed_updates=dp.resolve_used_update_types()
    )
    
    web.run_app(
        app,
        host='0.0.0.0',
        port=int(config.webhook_port),
        ssl_context=None
    )


async def start_bot_polling() -> None:
    """Запуск бота в режиме polling"""
    # Настройка startup и shutdown
    await bot.delete_webhook()
    # dp.startup.register(on_startup)
    # dp.shutdown.register(on_shutdown)

    sentry_logger.info("Запуск бота в режиме polling")
    
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(
        bot,
        allowed_updates=dp.resolve_used_update_types()
    )


def main(webhook: bool) -> None:
    """Основная функция запуска бота"""
    if webhook:
        asyncio.run(start_bot_webhook())
    else:
        asyncio.run(start_bot_polling())


if __name__ == '__main__':
    main(False)