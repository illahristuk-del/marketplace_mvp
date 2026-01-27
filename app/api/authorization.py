from datetime import datetime, timedelta, timezone
from typing import Annotated

from jose import jwt
from jose.exceptions import JWTError

from fastapi import Depends, APIRouter, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from pwdlib import PasswordHash
from pydantic_settings import BaseSettings

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.models.models import User
from app.schemas.auth_schema import Token
from app.schemas.user_schema import UserInPublic, UserCreate

class AuthSettings(BaseSettings):
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    class Config:
        env_file = ".env"
        env_prefix = "AUTH_"
        extra = "ignore"

settings = AuthSettings()

DBSession = Annotated[AsyncSession, Depends(get_session)]

password_hasher = PasswordHash.recommended()

def hash_password(password: str) -> str:
    return password_hasher.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hasher.verify(plain_password, hashed_password)

router = APIRouter(prefix="/auth", tags=["authorization"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

async def get_user_from_db(db: DBSession, username: str) -> User | None:
    stmt = select(User).where(User.username == username)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    return user

async def auth_user(db: DBSession, username: str, password: str) -> User | None:
    user = await get_user_from_db(db, username)

    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid username or password")
    return user

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    expire = now + (expires_delta or timedelta(minutes=settings.access_token_expire_minutes))
    to_encode.update({
        "type": "access",
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp())
        })
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)

def create_refresh_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    expire = now + (expires_delta or timedelta(days=settings.refresh_token_expire_days))
    to_encode.update({
        "type": "refresh",
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp())
        })
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: DBSession):
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        username = payload.get("sub")
        token_type = payload.get("type")
        if not username or token_type != "access":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not auth")
    
    user = await get_user_from_db(db, username)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username")
    
    return user

@router.post("/register", response_model=UserInPublic, status_code=201)
async def create_user(db: DBSession, user: UserCreate):
    existing_user = await get_user_from_db(db, user.username)

    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="username existing")
    
    new_user = User(
        first_name=user.first_name,
        last_name=user.last_name,
        username=user.username,
        email=user.email,
        phone_number=user.phone_number,
        hashed_password=hash_password(user.plain_password)
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user

@router.get("/me")
async def read_users_me(current_user: Annotated[User, Depends(get_current_user)]):
    return current_user

@router.post("/token", response_model=Token, status_code=200) 
async def login_for_tokens(db: DBSession, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = await get_user_from_db(db, form_data.username)

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credetials")
    
    access_token = create_access_token(data={"sub": form_data.username}, expires_delta=timedelta(minutes=30))
    refresh_token = create_refresh_token(data={"sub": form_data.username}, expires_delta=timedelta(days=7))

    user.refresh_token = refresh_token
    user.refresh_token_expire = datetime.now(timezone.utc) + timedelta(days=7)

    await db.commit()
    await db.refresh(user)

    return {"token_type": "bearer", "access_token": access_token, "refresh_token": refresh_token}

@router.post("/refresh", response_model=Token, status_code=200)
async def refresh_tokens(db: DBSession, refresh_token: str):
    try:
        payload = jwt.decode(refresh_token, settings.secret_key, algorithms=[settings.algorithm])
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    
    if payload.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")
    
    username = payload.get("sub")
    if not username:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token or username")
    
    user = await get_user_from_db(db, username)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    
    if user.refresh_token != refresh_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token invalid or revoked")
    
    if user.refresh_token_expire < datetime.now(timezone.utc):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token expired")
    
    new_access_token = create_access_token(data={"sub": user.username}, expires_delta=timedelta(minutes=30))
    new_refresh_token = create_refresh_token(data={"sub": user.username}, expires_delta=timedelta(days=7))
 
    user.refresh_token = new_refresh_token
    user.refresh_token_expire = datetime.now(timezone.utc) + timedelta(days=7)
    
    await db.commit()
    await db.refresh(user)

    return {"token_type": "bearer", "access_token": new_access_token, "refresh_token": new_refresh_token}