from pydantic import BaseModel, ConfigDict, Field, EmailStr
from typing import Annotated
from datetime import datetime

class UserInDb(BaseModel):
    id: int
    first_name: Annotated[str, Field(max_length=225)]
    last_name: Annotated[str, Field(max_length=225)]
    username: Annotated[str, Field(min_length=4, max_length=225)]
    email: Annotated[EmailStr, Field(max_length=225)]
    phone_number: Annotated[str, Field(max_length=30)]
    role: Annotated[str, Field(max_length=20)]
    hashed_password: Annotated[str, Field(max_length=225)]
    created_at: datetime
    refresh_token: Annotated[str | None, Field(max_length=225)] = None
    refresh_token_expire: datetime | None = None
    products: list

class UserInPublic(BaseModel):
    username: str
    phone_number: str
    email: EmailStr
    role: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class UserCreate(BaseModel):
    first_name: Annotated[str, Field(max_length=225)]
    last_name: Annotated[str, Field(max_length=225)]
    username: Annotated[str, Field(min_length=4, max_length=225)]
    email: Annotated[EmailStr, Field(max_length=225)]
    phone_number: Annotated[str, Field(max_length=30)]
    plain_password: Annotated[str, Field(min_length=8)]

