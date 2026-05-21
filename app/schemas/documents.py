from enum import Enum

from pydantic import BaseModel, Field


class PreparationMode(str, Enum):
    SEMANTIC = "semantic"


class ChunkSchema(BaseModel):
    chunk_id: str
    section: str
    semantic_summary: str
    keywords: list[str] = Field(default_factory=list)
    content: str
    suggested_embedding_text: str


class LLMPreparationResult(BaseModel):
    document_title: str
    document_summary: str
    chunks: list[ChunkSchema]


class PrepareDocumentResponse(BaseModel):
    document_id: str
    filename: str
    status: str = "prepared"
    document_title: str
    document_summary: str
    chunks: list[ChunkSchema]
