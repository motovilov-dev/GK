from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery

from db.repositories.user_repository import UserRepository
from db.repositories.gk_user_repository import GkUserRepository
from db.sessions import AsyncSessionFactory
from db.schemas.user import UserCreate, UserUpdate
from db.schemas.gk_user import GkUserUpdate
from db.models.user import GkUser, User
from utils.clients.GK_ApiClient import AsyncAPIClient

from loguru import logger


async def update_gk_user(user: User, token: str):
    try:
        async with AsyncAPIClient(token=token) as client:
            gk_user = await client.get_me()
            gk_user = gk_user.data
    except Exception as e:
        logger.error(f"update_gk_user: {e}")
        return None
    async with AsyncSessionFactory() as session:
        gk_repo = GkUserRepository(session=session)

        gk_update = GkUserUpdate(
            name=gk_user.name,
            first_name=gk_user.first_name,
            last_name=gk_user.last_name,
            email=gk_user.email,
            phone=gk_user.phone,
            sber_id=gk_user.sber_id,
            gazprom_id=gk_user.gazprom_id,
            aeroflot_id=gk_user.aeroflot_id,
            card_id=gk_user.card_id,
            passes_amount=gk_user.passes_amount,
            user_qr=gk_user.qr
        )

        return await gk_repo.update(user.gk_user.uuid, gk_update)



class GkAuthMiddleware(BaseMiddleware):
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
                user = await user_repository.get_with_gk_user(user_id)
                
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
                if not user.gk_user:
                    data['gk_auth'] = False
                    print(f"Пользователь {user_id} не зарегистрирован в gk")
                else:
                    print(f"Пользователь {user_id} зарегистрирован в gk")
                    gk_user = await update_gk_user(user, user.gk_user.token)
                    print(f"Пользователь {user_id} обновлен в gk")
                    data['gk_auth'] = True
                    data['gk_user'] = gk_user
                return await handler(event, data)
        except Exception as e:
            # Логируем ошибку и пропускаем запрос дальше
            logger.info(f"Ошибка при проверке пользователя gk: {e}")
            data['is_reg'] = False
            return await handler(event, data)