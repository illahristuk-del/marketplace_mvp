from fastapi import Depends
from db.session import get_session
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession

DBSession = Annotated[AsyncSession, Depends(get_session)] 