from typing import Optional, List
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from sqlalchemy.orm import selectinload

from db.models.gk_base_info import *

class HallsRepository:
    """
    Репозиторий для работы с залами и городами
    """
    
    def __init__(self, session: AsyncSession):
        """
        Инициализация репозитория с сессией БД
        
        Args:
            session: Асинхронная сессия SQLAlchemy
        """
        self.session = session
    
    async def get_by_gk_id(self, gk_id: int) -> Optional[Hall]:
        """
        Получение зала по gk_id
        
        Args:
            gk_id: gk_id зала
            
        Returns:
            Optional[Hall]: Найденный зал или None
        """
        query = select(Hall).where(Hall.gk_id == gk_id)
        result = await self.session.execute(query)
        return result.scalars().first()

    async def get_by_city_gk_id(self, city_gk_id: int) -> List[Hall]:
        """
        Получение залов по gk_id города со всей дополнительной информацией
        
        Args:
            city_gk_id: gk_id города
            
        Returns:
            List[Hall]: Список залов в указанном городе с подгруженными:
            - city_rel (город)
            - media (медиа)
            - services (услуги)
        """
        query = (
            select(Hall)
            .where(Hall.city_gk_id == city_gk_id)
            .options(
                selectinload(Hall.city_rel),  # Подгружаем связанный город
                selectinload(Hall.media),     # Подгружаем медиа
                selectinload(Hall.services)   # Подгружаем услуги
            )
        )
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Hall]:
        """
        Получение списка залов с пагинацией
        
        Args:
            skip: Количество пропускаемых записей
            limit: Максимальное количество возвращаемых записей
            
        Returns:
            List[Hall]: Список залов
        """
        query = select(Hall).offset(skip).limit(limit)
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def get_hall_with_relations(self, gk_id: int) -> Optional[Hall]:
        """
        Получение зала со всеми связанными данными (город, медиа, сервисы)
        
        Args:
            gk_id: gk_id зала
            
        Returns:
            Optional[Hall]: Найденный зал с отношениями или None
        """
        query = (
            select(Hall)
            .where(Hall.gk_id == gk_id)
            .options(
                selectinload(Hall.city_rel),
                selectinload(Hall.media),
                selectinload(Hall.services)
            )
        )
        result = await self.session.execute(query)
        return result.scalars().first()
    
    # Методы для работы с городами
    
    async def get_city_by_gk_id(self, gk_id: int) -> Optional[City]:
        """
        Получение города по gk_id
        
        Args:
            gk_id: gk_id города
            
        Returns:
            Optional[City]: Найденный город или None
        """
        query = select(City).where(City.gk_id == gk_id)
        result = await self.session.execute(query)
        return result.scalars().first()
    
    async def get_city_by_uuid(self, uuid: str) -> Optional[City]:
        """
        Получение города по uuid
        
        Args:
            uuid: UUID города
            
        Returns:
            Optional[City]: Найденный город или None
        """
        query = select(City).where(City.uuid == uuid)
        result = await self.session.execute(query)
        return result.scalars().first()
    
    async def get_all_cities(self, skip: int = 0, limit: int = 100) -> List[dict]:
        """
        Получение списка уникальных городов (по gk_id) с пагинацией
        
        Args:
            skip: Количество пропускаемых записей
            limit: Максимальное количество возвращаемых записей
            
        Returns:
            List[dict]: Список словарей с gk_id и name городов
            Пример: [{"gk_id": 1, "name": "Москва"}, ...]
        """
        try:
            query = (
                select(City.gk_id, City.name)
                .distinct(City.gk_id)  # Уникальность по gk_id
                .order_by(City.gk_id)  # Сортировка для стабильной пагинации
                .offset(skip)
                .limit(limit)
            )
            
            result = await self.session.execute(query)
            return [{"gk_id": row.gk_id, "name": row.name} for row in result.all()]
        except Exception as e:
            print(f"Ошибка при получении списка городов: {e}")
            return []
    
    async def get_city_with_halls(self, gk_id: int) -> Optional[City]:
        """
        Получение города со всеми его залами
        
        Args:
            gk_id: gk_id города
            
        Returns:
            Optional[City]: Найденный город с залами или None
        """
        query = (
            select(City)
            .where(City.gk_id == gk_id)
            .options(selectinload(City.halls))
        )
        result = await self.session.execute(query)
        return result.scalars().first()