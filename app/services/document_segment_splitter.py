from app.core.config import get_settings


class DocumentSegmentSplitter:
    def split(
        self,
        text: str,
        *,
        page_texts: list[str] | None = None,
    ) -> list[str]:
        settings = get_settings()
        max_chars = settings.max_chars_per_segment

        if len(text) <= max_chars:
            return [text]

        if page_texts:
            segments = self._split_by_pages(page_texts, max_chars, settings.segment_overlap_chars)
            if segments:
                return segments

        return self._split_by_paragraphs(text, max_chars, settings.segment_overlap_chars)

    def _split_by_pages(
        self,
        page_texts: list[str],
        max_chars: int,
        overlap: int,
    ) -> list[str]:
        segments: list[str] = []
        current_pages: list[str] = []
        current_len = 0

        for page_text in page_texts:
            if not page_text.strip():
                continue

            page_len = len(page_text)
            separator_len = 2 if current_pages else 0
            projected = current_len + separator_len + page_len

            if current_pages and projected > max_chars:
                segments.append("\n\n".join(current_pages))
                if overlap > 0 and current_pages:
                    overlap_text = current_pages[-1][-overlap:]
                    current_pages = [overlap_text, page_text] if overlap_text else [page_text]
                    current_len = len("\n\n".join(current_pages))
                else:
                    current_pages = [page_text]
                    current_len = page_len
            else:
                current_pages.append(page_text)
                current_len = projected

        if current_pages:
            segments.append("\n\n".join(current_pages))

        return segments if segments else []

    def _split_by_paragraphs(
        self,
        text: str,
        max_chars: int,
        overlap: int,
    ) -> list[str]:
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        if not paragraphs:
            return self._split_by_chars(text, max_chars, overlap)

        segments: list[str] = []
        current_parts: list[str] = []
        current_len = 0

        for paragraph in paragraphs:
            if len(paragraph) > max_chars:
                if current_parts:
                    segments.append("\n\n".join(current_parts))
                    current_parts = []
                    current_len = 0
                segments.extend(self._split_by_chars(paragraph, max_chars, overlap))
                continue

            separator_len = 2 if current_parts else 0
            projected = current_len + separator_len + len(paragraph)

            if current_parts and projected > max_chars:
                segments.append("\n\n".join(current_parts))
                if overlap > 0 and current_parts:
                    overlap_text = current_parts[-1][-overlap:]
                    current_parts = [overlap_text, paragraph] if overlap_text else [paragraph]
                    current_len = len("\n\n".join(current_parts))
                else:
                    current_parts = [paragraph]
                    current_len = len(paragraph)
            else:
                current_parts.append(paragraph)
                current_len = projected

        if current_parts:
            segments.append("\n\n".join(current_parts))

        return segments if segments else [text]

    def _split_by_chars(self, text: str, max_chars: int, overlap: int) -> list[str]:
        if len(text) <= max_chars:
            return [text]

        segments: list[str] = []
        start = 0
        while start < len(text):
            end = min(start + max_chars, len(text))
            segments.append(text[start:end])
            if end >= len(text):
                break
            start = max(end - overlap, start + 1)

        return segments
