from typing import AsyncGenerator, Optional
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from fastapi import Depends

from config import config

# Создаем базовый класс для моделей
Base = declarative_base()

# Создаем асинхронный движок SQLAlchemy
engine = create_async_engine(
    str(config.SQLALCHEMY_DATABASE_URI),
    echo=None,  # Вывод SQL-запросов в консоль при DEBUG=True
    pool_size=5,  # Минимальное количество соединений в пуле
    max_overflow=10,  # Максимальное количество дополнительных соединений
    pool_timeout=30,  # Таймаут ожидания соединения из пула (в секундах)
    pool_recycle=1800,  # Пересоздание соединения через 30 минут (в секундах)
    pool_pre_ping=True,  # Проверка соединения перед использованием
)

# Создаем фабрику сессий
AsyncSessionFactory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,  # Не истекать объекты после коммита
    autoflush=False,  # Не делать автоматический flush при запросах
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Зависимость для получения асинхронной сессии SQLAlchemy.
    Используется в эндпоинтах FastAPI через Depends.
    
    Yields:
        AsyncSession: Асинхронная сессия SQLAlchemy
    """
    async with AsyncSessionFactory() as session:
        try:
            yield session
        finally:
            await session.close()


# Функция для получения сессии вне контекста запроса (например, в фоновых задачах)
async def get_session() -> AsyncSession:
    """
    Создает и возвращает новую асинхронную сессию SQLAlchemy.
    Для использования вне контекста запроса.
    
    Returns:
        AsyncSession: Асинхронная сессия SQLAlchemy
    """
    return AsyncSessionFactory()


# Функция для инициализации базы данных (создание таблиц)
async def init_db() -> None:
    """
    Инициализирует базу данных, создавая все таблицы.
    Вызывается при запуске приложения.
    """
    async with engine.begin() as conn:
        # Создаем все таблицы, определенные в моделях
        await conn.run_sync(Base.metadata.create_all)