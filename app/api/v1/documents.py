from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.core.config import get_settings
from app.schemas.documents import PrepareDocumentResponse
from app.schemas.embeddings import EmbedDocumentRequest, EmbedDocumentResponse
from app.services.document_extractor import extract_from_text, extract_from_upload
from app.services.document_preparation import DocumentPreparationService
from app.services.embedding_service import EmbeddingService

router = APIRouter(tags=["documents"])

_preparation_service = DocumentPreparationService()


@router.post("/documents/prepare", response_model=PrepareDocumentResponse)
async def prepare_document(
    file: UploadFile | None = File(None),
    text: str | None = Form(None),
    mode: str = Form("semantic"),
    language: str = Form("es"),
    filename: str | None = Form(None),
) -> PrepareDocumentResponse:
    has_file = file is not None and file.filename
    has_text = text is not None and text.strip()

    if has_file and has_text:
        raise HTTPException(
            status_code=400,
            detail="Proporcione solo 'file' o 'text', no ambos",
        )
    if not has_file and not has_text:
        raise HTTPException(
            status_code=400,
            detail="Debe proporcionar 'file' o 'text'",
        )

    settings = get_settings()

    if has_file:
        content = await file.read()
        if len(content) > settings.max_upload_bytes:
            raise HTTPException(
                status_code=413,
                detail=f"Archivo demasiado grande. Máximo: {settings.max_upload_bytes} bytes",
            )
        await file.seek(0)
        extracted = await extract_from_upload(file)
    else:
        resolved_filename = filename or "inline.txt"
        extracted = extract_from_text(text, filename=resolved_filename)

    return await _preparation_service.prepare(
        document_text=extracted.text,
        filename=extracted.filename,
        mode=mode,
        language=language,
        page_texts=extracted.page_texts,
    )


@router.post(
    "/documents/{document_id}/embeddings",
    response_model=EmbedDocumentResponse,
)
async def create_embeddings(
    document_id: str,
    body: EmbedDocumentRequest,
) -> EmbedDocumentResponse:
    return await EmbeddingService.embed_document(document_id, body)
