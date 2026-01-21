from sqlalchemy.orm import relationship, mapped_column, Mapped, DeclarativeBase
from sqlalchemy import Integer, String, ForeignKey, TIMESTAMP, func, Float, Boolean, ARRAY, Text
from datetime import datetime
from typing import List

class Base(DeclarativeBase):
    pass

#User
class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(225), nullable=False)
    last_name: Mapped[str] = mapped_column(String(225), nullable=False)
    username: Mapped[str] = mapped_column(String(225), unique=True ,nullable=False)
    email: Mapped[str] = mapped_column(String(225), unique=True, nullable=False)
    phone_number: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)

    role: Mapped[str] = mapped_column(String(20), server_default="buyer")

    hashed_password: Mapped[str] = mapped_column(String(225))
    
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())

    refresh_token: Mapped[str | None] = mapped_column(String(225), nullable=True)
    refresh_token_expire: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)

    products: Mapped[List["Product"]] = relationship(back_populates="owner")

#Product
class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(225), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    price: Mapped[int] = mapped_column(Integer, nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())

    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)

    owner: Mapped["User"] = relationship(back_populates="products")
    category: Mapped["Category"] = relationship(back_populates="products")

#Category
class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(225), unique=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(225), unique=True, nullable=False)

    products: Mapped[List["Product"]] = relationship(back_populates="category")