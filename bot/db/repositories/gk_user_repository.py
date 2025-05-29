from typing import Optional, List
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from sqlalchemy.orm import selectinload

from db.models.user import GkUser
from db.schemas.gk_user import GkUserCreate, GkUserUpdate

class GkUserRepository:
    """
    Репозиторий для работы с пользователями GK
    """
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, gk_user_data: GkUserCreate) -> GkUser:
        """
        Создание нового пользователя GK
        
        Args:
            gk_user_data: Данные для создания пользователя GK
            
        Returns:
            GkUser: Созданный пользователь GK
        """
        gk_user = GkUser(**gk_user_data.dict())
        self.session.add(gk_user)
        await self.session.commit()
        await self.session.refresh(gk_user)
        return gk_user
    
    async def get_by_uuid(self, uuid: UUID) -> Optional[GkUser]:
        """
        Получение пользователя GK по UUID
        
        Args:
            uuid: UUID пользователя GK
            
        Returns:
            Optional[GkUser]: Найденный пользователь GK или None
        """
        query = select(GkUser).where(GkUser.uuid == uuid)
        result = await self.session.execute(query)
        return result.scalars().first()

    async def get_by_user_uuid(self, user_uuid: UUID) -> Optional[GkUser]:
        """
        Получение пользователя GK по UUID связанного пользователя
        
        Args:
            user_uuid: UUID связанного пользователя (User)
            
        Returns:
            Optional[GkUser]: Найденный пользователь GK или None
        """
        query = select(GkUser).where(GkUser.user_uuid == user_uuid)
        result = await self.session.execute(query)
        return result.scalars().first()

    async def get_by_gk_user_id(self, gk_user_id: int) -> Optional[GkUser]:
        """
        Получение пользователя GK по его ID в системе GK
        
        Args:
            gk_user_id: ID пользователя в системе GK
            
        Returns:
            Optional[GkUser]: Найденный пользователь GK или None
        """
        query = select(GkUser).where(GkUser.gk_user_id == gk_user_id)
        result = await self.session.execute(query)
        return result.scalars().first()
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[GkUser]:
        """
        Получение списка пользователей GK с пагинацией
        
        Args:
            skip: Количество пропускаемых записей
            limit: Максимальное количество возвращаемых записей
            
        Returns:
            List[GkUser]: Список пользователей GK
        """
        query = select(GkUser).offset(skip).limit(limit)
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def update(self, uuid: UUID, gk_user_data: GkUserUpdate) -> Optional[GkUser]:
        """
        Обновление данных пользователя GK
        
        Args:
            uuid: UUID пользователя GK
            gk_user_data: Данные для обновления
            
        Returns:
            Optional[GkUser]: Обновленный пользователь GK или None
        """
        update_data = gk_user_data.dict(exclude_unset=True)
        if not update_data:
            return await self.get_by_uuid(uuid)
            
        query = update(GkUser).where(GkUser.uuid == uuid).values(**update_data)
        await self.session.execute(query)
        await self.session.commit()
        return await self.get_by_uuid(uuid)
    
    async def delete(self, uuid: UUID) -> bool:
        """
        Удаление пользователя GK
        
        Args:
            uuid: UUID пользователя GK
            
        Returns:
            bool: True если пользователь удален, иначе False
        """
        gk_user = await self.get_by_uuid(uuid)
        if not gk_user:
            return False
            
        await self.session.delete(gk_user)
        await self.session.commit()
        return True