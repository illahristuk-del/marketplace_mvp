from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete

from app.models.models import Product
from app.schemas.product_schema import ProductCreate, ProductUpdate

async def create_product(db: AsyncSession, product_in: ProductCreate, owner_id: int):
    new_product = Product(**product_in.model_dump(), owner_id=owner_id)

    db.add(new_product)
    await db.commit()
    await db.refresh(new_product)

    return new_product

async def get_all_products(db: AsyncSession, skip: int = 0, limit: int = 20):
    result = await db.execute(select(Product).where(Product.is_active == True).offset(skip).limit(limit))
    
    return result.scalars().all()

async def get_product_by_id(db: AsyncSession, product_id: int):
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()

    return product

async def get_my_products(db: AsyncSession, owner_id: int):
    result = await db.execute(select(Product).where(Product.owner_id == owner_id))
    products = result.scalars().all()

    return products

async def update_product(db: AsyncSession, product_in: Product, data: ProductUpdate):
    update_data = data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(product_in, field, value)

    db.add(product_in)
    await db.commit()
    await db.refresh(product_in)

    return product_in
    
async def delete_product(db: AsyncSession, db_product: Product):
    await db.delete(db_product)
    await db.commit()

    return {"product": "deleted", "id": db_product.id}
    
    