from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from datetime import datetime
from db.models.gk_base_info import *

class ProductsRepository:
    """
    Репозиторий для работы с продуктами (только чтение)
    """
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_uuid(self, uuid: str) -> Optional[Products]:
        """
        Получение продукта по UUID
        
        Args:
            uuid: UUID продукта
            
        Returns:
            Optional[Products]: Найденный продукт или None
        """
        query = select(Products).where(Products.uuid == uuid)
        result = await self.session.execute(query)
        return result.scalars().first()
    
    async def get_by_gk_id(self, gk_id: int) -> Optional[Products]:
        """
        Получение продукта по gk_id
        
        Args:
            gk_id: GK ID продукта
            
        Returns:
            Optional[Products]: Найденный продукт или None
        """
        query = select(Products).where(Products.gk_id == gk_id)
        result = await self.session.execute(query)
        return result.scalars().first()
    
    async def get_all(
        self, 
        skip: int = 0, 
        limit: int = 100,
        foreign: Optional[bool] = None
    ) -> List[Products]:
        """
        Получение списка продуктов с фильтрацией
        
        Args:
            skip: Количество пропускаемых записей
            limit: Максимальное количество возвращаемых записей
            foreign: Фильтр по foreign (True/False/None - без фильтра)
            
        Returns:
            List[Products]: Список продуктов
        """
        query = select(Products)
        
        if foreign is not None:
            query = query.where(Products.foreign == foreign)
            
        query = query.offset(skip).limit(limit).order_by(Products.name)
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def get_active_products(self) -> List[Products]:
        """
        Получение активных продуктов (где count > 0)
        
        Returns:
            List[Products]: Список активных продуктов
        """
        query = select(Products).where(Products.count > 0).order_by(Products.name)
        result = await self.session.execute(query)
        return result.scalars().all()