from sqlalchemy.orm import relationship, mapped_column, Mapped, DeclarativeBase
from sqlalchemy import Integer, String, ForeignKey, TIMESTAMP, func, Boolean, Text, Enum as SQLEnum

from datetime import datetime
from typing import List

from enum import Enum as PyEnum

class Base(DeclarativeBase):
    pass

class UserRole(str, PyEnum):
    BUYER = "buyer"
    SELLER = "seller"
    ADMIN = "admin"

class OrderStatus(str, PyEnum):
    PENDING = "pending"
    PAID = "paid"
    SHIPPED = "shipped"   
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

#User
class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(225), nullable=False)
    last_name: Mapped[str] = mapped_column(String(225), nullable=False)
    username: Mapped[str] = mapped_column(String(225), unique=True ,nullable=False)
    email: Mapped[str] = mapped_column(String(225), unique=True, nullable=False)
    phone_number: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)

    role: Mapped[UserRole] = mapped_column(SQLEnum(UserRole), server_default="buyer", nullable=False)

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

#ItemInOrder
class OrderItem(Base):
    id: Mapped[int] = mapped_column(primary_key=True)

    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))

    price: Mapped[int] = mapped_column(Integer, nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, default=1)

    order: Mapped["Order"] = relationship(back_populates="items")
    product: Mapped["Product"] = relationship()

#Order
class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    
    status: Mapped[OrderStatus] = mapped_column(SQLEnum(OrderStatus), server_default="pending", nullable=False)

    total_price: Mapped[int] = mapped_column(Integer, nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())

    user: Mapped["User"] = relationship()
    items: Mapped["OrderItem"] = relationship(back_populates="order")