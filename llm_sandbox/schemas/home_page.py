from __future__ import annotations
from typing import Any, List, Optional
from pydantic import BaseModel, Field

class Pivot(BaseModel):
    hall_id: Optional[int]
    service_id: Optional[int]

class Service(BaseModel):
    id: Optional[int]
    name: Optional[str]
    icon: Optional[str]
    type_: Optional[str] = Field(None, alias='type')
    code: Optional[str]
    text: Optional[str]
    created_at: Optional[str]
    updated_at: Optional[str]
    content: Optional[List[Any] | Any]
    pivot: Optional[Pivot]

class Media(BaseModel):
    id: Optional[int]
    url: Optional[str]
    hall_id: Optional[int]

class City(BaseModel):
    id: Optional[int]
    name: Optional[str]
    code: Optional[str]
    iataCode: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    foreign: Optional[int]
    created_at: Optional[str]
    updated_at: Optional[str]

class HallType(BaseModel):
    id: Optional[int]
    created_at: Optional[str]
    updated_at: Optional[str]
    name: Optional[str]
    descricodeption: Optional[str]

class Data(BaseModel):
    id: Optional[int]
    priority: Optional[int]
    name: Optional[str]
    admin_name: Optional[str]
    city_id: Optional[int]
    type_: Optional[HallType] = Field(None, alias='from')
    description: Optional[str]
    working_time: Optional[str]
    location: Optional[str]
    user_id: Optional[int]
    created_at: Optional[str]
    updated_at: Optional[str]
    prefix: Optional[str]
    is_hidden: Optional[bool]
    htype_id: Optional[int]
    station_id: Optional[int]
    cities: Optional[City]
    media: Optional[List[Media]]
    services: Optional[List[Service]]

class Link(BaseModel):
    active: Optional[bool]
    label: Optional[str]
    url: Optional[str]

class Hall(BaseModel):
    current_page: Optional[int]
    data: Optional[List[Data]] # Основная ифнормация о залах
    first_page_url: Optional[str]
    from_: Optional[int] = Field(None, alias='from')  # Using Field with alias to handle 'from' keyword
    last_page: Optional[int]
    last_page_url: Optional[str]
    links: Optional[List[Link]]
    next_page_url: Optional[str]
    path: Optional[str]
    per_page: Optional[int]
    prev_page_url: Optional[str]
    to: Optional[int]
    total: Optional[int]

class Foreign(BaseModel):
    id: Optional[int]
    name: Optional[str]
    price: Optional[int]
    hall_id: Optional[int]
    short_description: Optional[str]
    description: Optional[str]
    created_at: Optional[str]
    updated_at: Optional[str]
    registry_id: Optional[int]
    prefix: Optional[str]
    deleted_at: Optional[Any]
    display: Optional[int]
    count: Optional[int]
    foreign: Optional[int]

class Regular(BaseModel):
    id: Optional[int]
    name: Optional[str]
    price: Optional[int]
    hall_id: Optional[int]
    short_description: Optional[str]
    description: Optional[str]
    created_at: Optional[str]
    updated_at: Optional[str]
    registry_id: Optional[int]
    prefix: Optional[str | Any]
    deleted_at: Optional[Any]
    display: Optional[int]
    count: Optional[int]
    foreign: Optional[int]

class Products(BaseModel):
    regular: Optional[List[Regular]]
    promo: Optional[List[Any] | Any]
    foreign: Optional[List[Foreign] | Any]

class Service(BaseModel):
    id: Optional[int]
    name: Optional[str]
    icon: Optional[str]
    type_: Optional[str] = Field(None, alias='type')
    code: Optional[str]
    text: Optional[str]
    created_at: Optional[str]
    updated_at: Optional[str]
    content: Optional[List[Any] | Any]

class HomePage(BaseModel):
    halls: Hall        # Бизнес залы с детилизациейй
    products: Products # Стоимость визитов в залы Рф/Зарубеж
    services: Any      # Весь список услуг (Смотрим услоги в детализации к залу)
