from pydantic import BaseModel

class Token(BaseModel):
    token_type: str
    access_token: str
    refresh_token: str | None

class TokenData(BaseModel):
    user_id: int
    username: str
    