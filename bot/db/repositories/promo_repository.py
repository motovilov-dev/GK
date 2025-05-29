from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from datetime import datetime
from db.models.gk_base_info import *

class PromoServicesRepository:
    """
    Репозиторий для работы с промо-услугами (только чтение)
    """
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_uuid(self, uuid: str) -> Optional[PromoServices]:
        """
        Получение промо-услуги по UUID
        
        Args:
            uuid: UUID промо-услуги
            
        Returns:
            Optional[PromoServices]: Найденная промо-услуга или None
        """
        query = select(PromoServices).where(PromoServices.uuid == uuid)
        result = await self.session.execute(query)
        return result.scalars().first()
    
    async def get_by_gk_id(self, gk_id: int) -> Optional[PromoServices]:
        """
        Получение промо-услуги по gk_id
        
        Args:
            gk_id: GK ID промо-услуги
            
        Returns:
            Optional[PromoServices]: Найденная промо-услуга или None
        """
        query = select(PromoServices).where(PromoServices.gk_id == gk_id)
        result = await self.session.execute(query)
        return result.scalars().first()
    
    async def get_all_active(self) -> List[PromoServices]:
        """
        Получение всех активных промо-услуг
        
        Returns:
            List[PromoServices]: Список активных промо-услуг
        """
        query = select(PromoServices).where(PromoServices.active == True).order_by(PromoServices.name)
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def get_all(
        self, 
        skip: int = 0, 
        limit: int = 100,
        active: Optional[bool] = None
    ) -> List[PromoServices]:
        """
        Получение списка промо-услуг с фильтрацией
        
        Args:
            skip: Количество пропускаемых записей
            limit: Максимальное количество возвращаемых записей
            active: Фильтр по активности (True/False/None - без фильтра)
            
        Returns:
            List[PromoServices]: Список промо-услуг
        """
        query = select(PromoServices)
        
        if active is not None:
            query = query.where(PromoServices.active == active)
            
        query = query.offset(skip).limit(limit).order_by(PromoServices.name)
        result = await self.session.execute(query)
        return result.scalars().all()