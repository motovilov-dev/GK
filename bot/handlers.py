from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram import Dispatcher

# Создание основного роутера
main_router = Router(name='main')


@main_router.message(Command('start'))
async def cmd_start(message: Message) -> None:
    """Обработчик команды /start"""
    await message.answer(
        'Привет! Я бот на aiogram 3.x\n'
        'Используйте /help для получения списка команд.'
    )


@main_router.message(Command('help'))
async def cmd_help(message: Message) -> None:
    """Обработчик команды /help"""
    help_text = (
        'Доступные команды:\n'
        '/start - Начать работу с ботом\n'
        '/help - Показать это сообщение'
    )
    await message.answer(help_text)


@main_router.message(F.text)
async def handle_text(message: Message) -> None:
    """Обработчик текстовых сообщений"""
    await message.answer(f'Вы написали: {message.text}')


def setup_routers(dp: Dispatcher) -> None:
    """Подключение всех роутеров к диспетчеру"""
    dp.include_router(main_router)