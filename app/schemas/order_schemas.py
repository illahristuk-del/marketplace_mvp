from pydantic import BaseModel, ConfigDict, Field
from typing import Annotated
from datetime import datetime

from app.models.models import OrderStatus

class OrderItemRead(BaseModel):
    id: int
    product_id: int | None
    quantity: Annotated[int, Field(ge=1)]
    price_at_purchase: Annotated[int, Field(ge=0)]
    
    model_config = ConfigDict(from_attributes=True)

class OrderItemCreate(BaseModel):
    product_id: int
    quantity: Annotated[int, Field(ge=1)] = 1

class OrderInDB(BaseModel):
    id: int
    user_id: int
    status: OrderStatus
    total_price: Annotated[int, Field(ge=0)]
    created_at: datetime
    items: list[OrderItemRead]

    model_config = ConfigDict(from_attributes=True)

class OrderCreate(BaseModel):
    items: Annotated[list[OrderItemCreate], Field(min_length=1)]

class OrderUpdateStatus(BaseModel):
    status: OrderStatus

class OrderPublic(BaseModel):
    id: int
    status: OrderStatus
    total_price: int
    created_at: datetime
    items: list[OrderItemRead]

    model_config = ConfigDict(from_attributes=True)