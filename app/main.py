from fastapi import FastAPI
from app.api.authorization import router as auth_router

app = FastAPI()

app.include_router(auth_router)