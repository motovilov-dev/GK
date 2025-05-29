from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime

class GkUserBase(BaseModel):
    user_uuid: UUID
    gk_user_id: int
    name: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    password: Optional[str] = None
    token: Optional[str] = None
    role: Optional[int] = None
    sber_id: Optional[str] = None
    gazprom_id: Optional[str] = None
    aeroflot_id: Optional[str] = None
    card_id: Optional[str] = None
    passes_amount: int = 0
    user_qr: Optional[str] = None

class GkUserCreate(GkUserBase):
    pass

class GkUserUpdate(BaseModel):
    name: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    password: Optional[str] = None
    token: Optional[str] = None
    role: Optional[int] = None
    sber_id: Optional[str] = None
    gazprom_id: Optional[str] = None
    aeroflot_id: Optional[str] = None
    card_id: Optional[str] = None
    passes_amount: Optional[int] = None
    user_qr: Optional[str] = None

class GkUserInDB(GkUserBase):
    uuid: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True