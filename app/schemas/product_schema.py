from pydantic import BaseModel, ConfigDict, Field, EmailStr
from typing import Annotated
from datetime import datetime

class ProductInDB(BaseModel):
    id: int
    title: Annotated[str, Field(max_length=225)]
    description: Annotated[str | None, Field()] = None
    price: Annotated[int, Field(ge=0)]
    quantity: Annotated[int, Field(ge=0)]
    is_active: bool
    created_at: datetime

    owner_id: int
    category_id: int | None = None

    model_config = ConfigDict(from_attributes=True)

class ProductCreate(BaseModel): 
    title: Annotated[str, Field(max_length=225)]
    description: Annotated[str | None, Field()] = None
    price: Annotated[int, Field(ge=0)]
    quantity: Annotated[int, Field(ge=0)]
    is_active: bool = True
    category_id: int | None = None

class ProductUpdate(BaseModel):
    title: Annotated[str | None, Field(max_length=225)] = None
    description: Annotated[str | None, Field()] = None
    price: Annotated[int | None, Field(ge=0)] = None
    quantity: Annotated[int | None, Field(ge=0)] = None
    is_active: bool | None = None
    category_id: int | None = None

class ProductInPublic(BaseModel):
    id: int
    title: Annotated[str, Field(max_length=225)]
    description: Annotated[str | None, Field()] = None
    price: Annotated[int, Field(ge=0)]
    quantity: Annotated[int, Field(ge=0)]
    is_active: bool = True
    category_id: int | None = None
