from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class RewardItem(BaseModel):
    id: int
    active: int
    name: str
    code: str
    denomination: str
    description: Optional[str]
    created_at: datetime
    updated_at: datetime


class RewardResponse(BaseModel):
    success: bool
    data: List[RewardItem]