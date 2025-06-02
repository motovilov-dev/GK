from typing import List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field

class Order(BaseModel):
    """Order model"""
    id: int
    quantity: int
    total: Optional[str]
    status: Optional[str]
    user_id: int
    product_id: int
    created_at: datetime
    updated_at: datetime
    email: Optional[str]
    bank: Optional[str]
    affiliate: Optional[int]
    hidden: Optional[int]
    partner_id: Any
    iway_transaction_id: Any
    order_meta: Any
    certificates: Any
    product: Any


class OrdersResponse(BaseModel):
    """Response model for orders list"""
    success: bool
    data: List[Order]