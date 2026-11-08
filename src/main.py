from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from src.api.router import api_router
from src.core.config import get_settings
from src.models.base import Base
from src.db.session import engine


@asynccontextmanager
async def lifespan(_: FastAPI):
    from src.models.task import TaskORM
    Base.metadata.create_all(bind=engine)
    yield


settings = get_settings()
app = FastAPI(lifespan=lifespan)


app.add_middleware(
     CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)


app.include_router(api_router)
