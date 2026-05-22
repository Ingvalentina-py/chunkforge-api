from fastapi import APIRouter

from app.schemas.embeddings import EmbedTextRequest, EmbedTextResponse
from app.services.embedding_service import EmbeddingService

router = APIRouter(tags=["embed"])


@router.post("/embed", response_model=EmbedTextResponse)
async def embed_text(body: EmbedTextRequest) -> EmbedTextResponse:
    return await EmbeddingService.embed_text(body)
