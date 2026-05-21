import asyncio

from fastapi import HTTPException
from sentence_transformers import SentenceTransformer

from app.core.config import get_settings
from app.schemas.embeddings import (
    EmbedDocumentRequest,
    EmbedDocumentResponse,
    VectorPayloadSchema,
    VectorResultSchema,
)

_model: SentenceTransformer | None = None
_model_lock = asyncio.Lock()


class EmbeddingService:
    @classmethod
    def _load_model(cls) -> SentenceTransformer:
        global _model
        if _model is None:
            settings = get_settings()
            _model = SentenceTransformer(settings.embedding_model)
        return _model

    @classmethod
    def warmup(cls) -> None:
        cls._load_model()

    @classmethod
    async def _get_model(cls) -> SentenceTransformer:
        if _model is not None:
            return _model
        async with _model_lock:
            if _model is not None:
                return _model
            return await asyncio.to_thread(cls._load_model)

    @classmethod
    def _validate_embedding_model(cls, request: EmbedDocumentRequest) -> None:
        settings = get_settings()
        if (
            request.embedding_model is not None
            and request.embedding_model != settings.embedding_model
        ):
            raise HTTPException(
                status_code=422,
                detail=(
                    f"embedding_model no coincide con el configurado. "
                    f"Esperado: {settings.embedding_model}"
                ),
            )

    @classmethod
    def _encode(cls, texts: list[str]) -> list[list[float]]:
        model = cls._load_model()
        embeddings = model.encode(texts, normalize_embeddings=True)
        return [vector.tolist() for vector in embeddings]

    @classmethod
    async def embed_document(
        cls,
        document_id: str,
        request: EmbedDocumentRequest,
    ) -> EmbedDocumentResponse:
        cls._validate_embedding_model(request)

        try:
            model = await cls._get_model()
        except Exception as exc:
            raise HTTPException(
                status_code=500,
                detail=f"No se pudo cargar el modelo de embeddings: {exc}",
            ) from exc

        texts = [chunk.text for chunk in request.chunks]

        try:
            vectors = await asyncio.to_thread(cls._encode, texts)
        except Exception as exc:
            raise HTTPException(
                status_code=500,
                detail=f"Error al generar embeddings: {exc}",
            ) from exc

        settings = get_settings()
        dimensions = model.get_sentence_embedding_dimension()

        results: list[VectorResultSchema] = []
        for chunk, vector in zip(request.chunks, vectors):
            payload = VectorPayloadSchema(
                text=chunk.text,
                section=chunk.metadata.section,
                keywords=chunk.metadata.keywords,
                source=request.source,
            )
            results.append(
                VectorResultSchema(
                    chunk_id=chunk.chunk_id,
                    vector=vector,
                    payload=payload,
                )
            )

        return EmbedDocumentResponse(
            document_id=document_id,
            embedding_model=settings.embedding_model,
            dimensions=dimensions,
            total_chunks=len(results),
            vectors=results,
        )
