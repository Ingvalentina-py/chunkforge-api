from app.schemas.documents import ChunkSchema, LLMPreparationResult


class PreparationResultMerger:
    def merge(self, results: list[LLMPreparationResult]) -> LLMPreparationResult:
        if not results:
            raise ValueError("No hay resultados para fusionar")

        if len(results) == 1:
            return results[0]

        document_title = self._resolve_title(results)
        document_summary = self._resolve_summary(results)
        merged_chunks = self._merge_chunks(results)

        return LLMPreparationResult(
            document_title=document_title,
            document_summary=document_summary,
            chunks=merged_chunks,
        )

    def _resolve_title(self, results: list[LLMPreparationResult]) -> str:
        for result in results:
            if result.document_title.strip():
                return result.document_title.strip()
        return "Untitled Document"

    def _resolve_summary(self, results: list[LLMPreparationResult]) -> str:
        summaries = [r.document_summary.strip() for r in results if r.document_summary.strip()]
        if not summaries:
            return ""
        if len(summaries) == 1:
            return summaries[0]
        return " ".join(summaries)

    def _merge_chunks(self, results: list[LLMPreparationResult]) -> list[ChunkSchema]:
        merged: list[ChunkSchema] = []
        counter = 1

        for result in results:
            for chunk in result.chunks:
                merged.append(
                    chunk.model_copy(
                        update={"chunk_id": f"chunk_{counter:03d}"},
                    )
                )
                counter += 1

        return merged
