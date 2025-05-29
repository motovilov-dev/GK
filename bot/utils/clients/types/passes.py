from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class Hall(BaseModel):
    id: int
    priority: Optional[int] = None
    name: Optional[str]
    admin_name: Optional[str]
    city_id: Optional[int]
    type: Optional[str] = None
    description: Optional[str] = None
    working_time: Optional[str]
    location: Optional[str]
    user_id: Optional[int]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    prefix: Optional[str]
    is_hidden: Optional[int]
    htype_id: Optional[int] = None
    station_id: Optional[int] = None


class Pass(BaseModel):
    start_time: Optional[str]
    updated_at: Optional[datetime]
    created_at: Optional[datetime]
    hall_id: Optional[int]
    product_id: Optional[int] = None
    user_id: Optional[int]
    pass_limit: Optional[int]
    status: Optional[str]
    hash: Optional[str] = None
    id: Optional[int]
    order_id: Optional[int] = None
    table_number: Optional[str] = None
    description: Optional[str] = None
    code: Optional[str] = None
    user_name: Optional[str]
    queue_id: Optional[int] = None
    bank: Optional[str]
    expiration_at: Optional[str] = None
    start_at: Optional[str] = None
    hidden: Optional[int]
    boarding_pass_id: Optional[int] = None
    station_id: Optional[int] = None
    qr: Optional[str]
    hall: Optional[Hall]


class Data(BaseModel):
    passes: List[Optional[Pass]]


class PassesResponse(BaseModel):
    success: bool
    data: Data