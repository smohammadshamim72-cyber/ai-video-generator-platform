from __future__ import annotations

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import settings
from app.routes.generation import router as generation_router
from app.routes.realtime import router as realtime_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    os.makedirs(settings.storage_dir, exist_ok=True)
    yield


app = FastAPI(title=settings.app_name, version="1.0.0", lifespan=lifespan)
app.include_router(generation_router)
app.include_router(realtime_router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "ai-video-generator"}
