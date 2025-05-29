from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional
from uuid import UUID

class UserBase(BaseModel):
    """Базовая схема пользователя с общими полями"""
    telegram_id: int
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    language_code: Optional[str] = None
    is_premium: Optional[bool] = False
    is_bot: Optional[bool] = False
    is_active: Optional[bool] = True

class UserCreate(BaseModel):
    """Схема для создания пользователя"""
    telegram_id: int
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    language_code: Optional[str] = None
    is_premium: Optional[bool] = False
    is_bot: Optional[bool] = False
    is_active: Optional[bool] = True

class UserUpdate(BaseModel):
    """Схема для обновления пользователя"""
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    language_code: Optional[str] = None
    is_premium: Optional[bool] = False
    is_bot: Optional[bool] = False
    is_active: Optional[bool] = True

class UserInDB(UserBase):
    """Схема пользователя с данными из БД"""
    uuid: UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class UserResponse(UserInDB):
    """Схема для ответа API"""
    pass