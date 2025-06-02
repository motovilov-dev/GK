from datetime import datetime

from pydantic import BaseModel
from typing import List, Optional, Any


class PromoService(BaseModel):
    id: int
    name: Optional[str]
    code: Optional[str]
    description: Optional[str]

class Promo(BaseModel):
    id: int
    quantity: int
    codes: list[str]
    status: str
    created_at: datetime
    updated_at: str
    promo_service: PromoService

class DataModel(BaseModel):
    certificates: List[Any]
    promo: Optional[List[Optional[Promo]]]

class PromoResponse(BaseModel):
    success: bool
    data: Optional[DataModel]