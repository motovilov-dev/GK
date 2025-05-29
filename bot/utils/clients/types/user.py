from datetime import datetime
from typing import List, Optional, Any
from pydantic import BaseModel


class PromoService(BaseModel):
    id: int
    active: int
    name: str


class Role(BaseModel):
    id: int
    name: str
    created_at: datetime
    updated_at: datetime


class DiscountCard(BaseModel):
    first_name: str
    last_name: str
    passes_amount: int
    notice: str
    unlimited: bool


class UserData(BaseModel):
    id: int
    name: Optional[str] = None
    email: str
    phone: str
    role_id: int
    bonuses: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    sber_id: Optional[str] = None
    gazprom_id: Optional[str] = None
    aeroflot_id: Optional[str] = None
    card_id: str
    referral_id: Optional[str] = None
    external_id: Optional[str] = None
    passes_amount: int
    first_name: str
    last_name: str
    patronymic: Optional[str] = None
    name_changed_at: Optional[datetime] = None
    first_name_changed_at: Optional[datetime] = None
    discount_card: DiscountCard
    promo: Optional[str] = None
    promo_services: List[PromoService]
    qr: str
    role: Role
    promo: Any
    promos: List[Any]  # Уточните тип, если promos имеет другую структуру
    legal_entity: Optional[Any] = None
    certificates: List[Any]  # Уточните тип, если certificates имеет другую структуру
    promos_free: List[Any]  # Уточните тип, если promos_free имеет другую структуру


class UserInfoResponse(BaseModel):
    success: bool
    data: UserData