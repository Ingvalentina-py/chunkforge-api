import uuid

from fastapi import HTTPException

from app.prompts.document_preparation import SYSTEM_PROMPT, build_user_prompt
from app.schemas.documents import LLMPreparationResult, PrepareDocumentResponse, PreparationMode
from app.services.deepseek import complete_prompt_json
from app.services.document_segment_splitter import DocumentSegmentSplitter
from app.services.preparation_merger import PreparationResultMerger


class DocumentPreparationService:
    def __init__(self) -> None:
        self._splitter = DocumentSegmentSplitter()
        self._merger = PreparationResultMerger()

    async def prepare(
        self,
        *,
        document_text: str,
        filename: str,
        mode: str,
        language: str,
        page_texts: list[str] | None = None,
    ) -> PrepareDocumentResponse:
        if mode != PreparationMode.SEMANTIC:
            raise HTTPException(
                status_code=422,
                detail=f"Modo no soportado: {mode}. Use: {PreparationMode.SEMANTIC}",
            )

        segments = self._splitter.split(document_text, page_texts=page_texts)
        part_total = len(segments)
        results: list[LLMPreparationResult] = []

        for index, segment_text in enumerate(segments, start=1):
            result = await self._process_segment(
                segment_text,
                language=language,
                mode=mode,
                part_index=index if part_total > 1 else None,
                part_total=part_total if part_total > 1 else None,
            )
            results.append(result)

        merged = self._merger.merge(results)

        return PrepareDocumentResponse(
            document_id=f"doc_{uuid.uuid4().hex[:12]}",
            filename=filename,
            status="prepared",
            document_title=merged.document_title,
            document_summary=merged.document_summary,
            chunks=merged.chunks,
        )

    async def _process_segment(
        self,
        segment_text: str,
        *,
        language: str,
        mode: str,
        part_index: int | None,
        part_total: int | None,
    ) -> LLMPreparationResult:
        user_prompt = build_user_prompt(
            segment_text,
            language=language,
            mode=mode,
            part_index=part_index,
            part_total=part_total,
        )

        last_error: Exception | None = None
        for _ in range(2):
            try:
                return await complete_prompt_json(
                    user_prompt,
                    system_prompt=SYSTEM_PROMPT,
                )
            except ValueError as exc:
                last_error = exc

        raise HTTPException(
            status_code=502,
            detail=f"Error al procesar el documento con DeepSeek: {last_error}",
        )
