from pydantic import BaseModel, Field, field_validator


class ChunkMetadataSchema(BaseModel):
    section: str = ""
    keywords: list[str] = Field(default_factory=list)


class ChunkInputSchema(BaseModel):
    chunk_id: str
    text: str
    metadata: ChunkMetadataSchema = Field(default_factory=ChunkMetadataSchema)

    @field_validator("text")
    @classmethod
    def text_not_empty(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("text no puede estar vacío")
        return value


class EmbedDocumentRequest(BaseModel):
    chunks: list[ChunkInputSchema] = Field(min_length=1)
    embedding_model: str | None = None
    source: str | None = None

    @field_validator("chunks")
    @classmethod
    def unique_chunk_ids(cls, chunks: list[ChunkInputSchema]) -> list[ChunkInputSchema]:
        ids = [chunk.chunk_id for chunk in chunks]
        if len(ids) != len(set(ids)):
            raise ValueError("chunk_id duplicados no permitidos")
        return chunks


class VectorPayloadSchema(BaseModel):
    text: str
    section: str
    keywords: list[str]
    source: str | None = None


class VectorResultSchema(BaseModel):
    chunk_id: str
    vector: list[float]
    payload: VectorPayloadSchema


class EmbedDocumentResponse(BaseModel):
    document_id: str
    embedding_model: str
    dimensions: int
    total_chunks: int
    vectors: list[VectorResultSchema]
