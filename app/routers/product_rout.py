from typing import Annotated
from fastapi import Depends, APIRouter, HTTPException, status, Query

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import DBSession, AllowAdmin, AllowSeller, AllowAll
from app.models.models import User, Product
from app.schemas.product_schema import ProductCreate, ProductUpdate, ProductInDB, ProductInPublic
from app.crud import product as prod_crud

router = APIRouter(prefix="/product", tags=["products"])

@router.post("/", response_model=ProductInDB, status_code=201)
async def create_product(product_data: ProductCreate, db: DBSession, current_user: AllowSeller):
    return await prod_crud.create_product(db=db, product_in=product_data, owner_id=current_user.id)
    
@router.get("/my", response_model=list[ProductInDB], status_code=200)
async def get_my_products(db: DBSession, current_user: AllowAll):
    product = await prod_crud.get_my_products(db=db, owner_id=current_user.id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    
    return product

@router.get("/{product_id}", response_model=ProductInPublic, status_code=200)
async def get_product_by_id(db: DBSession, product_id: int):
    product = await prod_crud.get_product_by_id(db=db, product_id=product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    
    return product

@router.put("/{product_id}", response_model=ProductInDB, status_code=200)
async def update_product(db: DBSession, current_user: AllowAll, update_data: ProductUpdate, product_id: int):
    product = await prod_crud.get_product_by_id(db=db, product_id=product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    
    if current_user.id != product.owner_id and current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Fodbidden")
    
    new_product_data = await prod_crud.update_product(db=db, product_in=product, data=update_data)

    return new_product_data

@router.delete("/{product_id}", status_code=200)
async def update_product(db: DBSession, current_user: AllowAll, product_id: int):
    product = await prod_crud.get_product_by_id(db=db, product_id=product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    
    if current_user.id != product.owner_id and current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Fodbidden")
    
    await prod_crud.delete_product(db=db, db_product=product)

    return {"status": "done", "product_id": product.id} 