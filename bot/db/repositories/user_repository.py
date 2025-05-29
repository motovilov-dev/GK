from typing import Optional, List, Union
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from sqlalchemy.orm import selectinload

from db.models.user import User
from db.schemas.user import UserCreate, UserUpdate

class UserRepository:
    """
    Репозиторий для работы с пользователями
    """
    
    def __init__(self, session: AsyncSession):
        """
        Инициализация репозитория с сессией БД
        
        Args:
            session: Асинхронная сессия SQLAlchemy
        """
        self.session = session
    
    async def create(self, user_data: UserCreate) -> User:
        """
        Создание нового пользователя
        
        Args:
            user_data: Данные для создания пользователя
            
        Returns:
            User: Созданный пользователь
        """
        user = User(**user_data.dict())
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user
    
    async def get_by_uuid(self, uuid: UUID) -> Optional[User]:
        """
        Получение пользователя по UUID
        
        Args:
            uuid: UUID пользователя
            
        Returns:
            Optional[User]: Найденный пользователь или None
        """
        query = select(User).where(User.uuid == uuid)
        result = await self.session.execute(query)
        return result.scalars().first()

    async def get_by_tg_id(self, tg_id: int) -> Optional[User]:
        """
        Получение пользователя по telegram_id

        Args:
            telegram_id: ID пользователя в Telegram

        Returns:
            Optional[User]: Найденный пользователь или None
        """
        query = select(User).where(User.telegram_id == tg_id)
        result = await self.session.execute(query)
        return result.scalars().first()

    async def get_with_gk_user(self, user_id: Union[UUID, int]) -> Optional[User]:
        """
        Получение пользователя вместе с связанным GkUser
        
        Args:
            user_id: UUID пользователя или telegram_id
            
        Returns:
            Optional[User]: Пользователь с загруженным gk_user или None
        """
        if isinstance(user_id, UUID):
            query = select(User).where(User.uuid == user_id)
        else:
            query = select(User).where(User.telegram_id == user_id)
        
        query = query.options(selectinload(User.gk_user))
        result = await self.session.execute(query)
        return result.scalars().first()
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[User]:
        """
        Получение списка пользователей с пагинацией
        
        Args:
            skip: Количество пропускаемых записей
            limit: Максимальное количество возвращаемых записей
            
        Returns:
            List[User]: Список пользователей
        """
        query = select(User).offset(skip).limit(limit)
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def update(self, uuid: UUID, user_data: UserUpdate) -> Optional[User]:
        """
        Обновление данных пользователя
        
        Args:
            uuid: UUID пользователя
            user_data: Данные для обновления
            
        Returns:
            Optional[User]: Обновленный пользователь или None
        """
        update_data = user_data.dict(exclude_unset=True)
        if not update_data:
            return await self.get_by_uuid(uuid)
            
        query = update(User).where(User.uuid == uuid).values(**update_data)
        await self.session.execute(query)
        await self.session.commit()
        return await self.get_by_uuid(uuid)
    
    async def delete(self, uuid: UUID) -> bool:
        """
        Удаление пользователя
        
        Args:
            uuid: UUID пользователя
            
        Returns:
            bool: True если пользователь удален, иначе False
        """
        user = await self.get_by_uuid(uuid)
        if not user:
            return False
            
        await self.session.delete(user)
        await self.session.commit()
        return True