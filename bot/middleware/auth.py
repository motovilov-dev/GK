from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery

from db.repositories.user_repository import UserRepository
from db.sessions import AsyncSessionFactory
from db.schemas.user import UserCreate, UserUpdate

from loguru import logger


class AuthMiddleware(BaseMiddleware):
    """Middleware для аутентификации пользователей и проверки их регистрации"""
    
    async def __call__(
        self,
        handler: Callable[[Message | CallbackQuery, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:
        """Проверяет регистрацию пользователя и добавляет информацию в data"""
        user_id = event.from_user.id
        
        try:
            # Создаем сессию для каждого запроса
            async with AsyncSessionFactory() as session:
                user_repository = UserRepository(session)
                # Проверяем регистрацию пользователя
                user = await user_repository.get_by_tg_id(user_id)
                
                # Если пользователь зарегистрирован, добавляем его данные
                if not user:
                    user = await user_repository.create(
                        UserCreate(
                            telegram_id=user_id,
                            username=event.from_user.username,
                            first_name=event.from_user.first_name,
                            last_name=event.from_user.last_name,
                            language_code=event.from_user.language_code,
                            is_premium=event.from_user.is_premium,
                            is_bot=event.from_user.is_bot,
                            is_active=True
                        )
                    )
                else:
                    user = await user_repository.update(
                        user.uuid,
                        UserUpdate(
                            username=event.from_user.username,
                            first_name=event.from_user.first_name,
                            last_name=event.from_user.last_name,
                            language_code=event.from_user.language_code,
                            is_active=True
                        )
                    )
                
                data['user'] = user
                
                return await handler(event, data)
        except Exception as e:
            # Логируем ошибку и пропускаем запрос дальше
            logger.info(f"Ошибка при проверке пользователя tg: {e}")
            data['is_reg'] = False
            return await handler(event, data)