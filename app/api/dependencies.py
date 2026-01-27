from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated

from app.db.session import get_session
from app.models.models import User, UserRole
from app.api.authorization import get_current_user

DBSession = Annotated[AsyncSession, Depends(get_session)] 
CurrentUser = Annotated[User, Depends(get_current_user)]

class RoleChecker:
    def __init__(self, allowed_roles: list[UserRole]):
            self.allowed_roles = allowed_roles

    def __call__(self, user: CurrentUser):
        if user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: insufficient permissions"
            )
        return user

AllowAdmin = Annotated[User, Depends(RoleChecker([UserRole.ADMIN]))]
AllowSeller = Annotated[User, Depends(RoleChecker([UserRole.SELLER, UserRole.ADMIN]))]
AllowAll = Annotated[User, Depends(RoleChecker([UserRole.BUYER, UserRole.SELLER, UserRole.ADMIN]))]