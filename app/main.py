import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.services.embedding_service import EmbeddingService


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        await asyncio.to_thread(EmbeddingService.warmup)
    except Exception:
        pass
    yield


app = FastAPI(
    title="ChunkForge API",
    version="0.1.0",
    lifespan=lifespan,
)

_settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=_settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root() -> dict[str, str]:
    return {
        "service": "ChunkForge API",
        "status": "ok",
        "message": "La API está funcionando correctamente.",
        "version": "0.1.0",
        "docs": "/docs",
        "api": "/api/v1",
    }


app.include_router(api_router, prefix="/api/v1")
