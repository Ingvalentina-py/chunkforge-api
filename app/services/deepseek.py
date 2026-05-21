import json
import re

from openai import AsyncOpenAI
from pydantic import ValidationError

from app.core.config import get_settings
from app.schemas.documents import LLMPreparationResult

_client: AsyncOpenAI | None = None

_JSON_FENCE_PATTERN = re.compile(
    r"^```(?:json)?\s*\n?(.*?)\n?```\s*$",
    re.DOTALL | re.IGNORECASE,
)


def _get_client() -> AsyncOpenAI:
    global _client
    if _client is None:
        settings = get_settings()
        _client = AsyncOpenAI(
            api_key=settings.deepseek_api_key,
            base_url=settings.deepseek_base_url,
        )
    return _client


def _parse_json_content(raw: str) -> dict:
    text = raw.strip()
    fence_match = _JSON_FENCE_PATTERN.match(text)
    if fence_match:
        text = fence_match.group(1).strip()
    return json.loads(text)


async def complete_prompt(
    prompt: str,
    *,
    system_prompt: str | None = None,
    max_tokens: int | None = None,
) -> str:
    settings = get_settings()
    messages: list[dict[str, str]] = []

    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})

    messages.append({"role": "user", "content": prompt})

    kwargs: dict = {
        "model": settings.deepseek_model,
        "messages": messages,
    }
    if max_tokens is not None:
        kwargs["max_tokens"] = max_tokens

    response = await _get_client().chat.completions.create(**kwargs)

    content = response.choices[0].message.content
    if content is None:
        raise RuntimeError("DeepSeek devolvió una respuesta vacía")

    return content


async def complete_prompt_json(
    prompt: str,
    *,
    system_prompt: str | None = None,
    max_tokens: int | None = None,
) -> LLMPreparationResult:
    settings = get_settings()
    effective_max_tokens = max_tokens if max_tokens is not None else settings.deepseek_max_tokens

    messages: list[dict[str, str]] = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    response = await _get_client().chat.completions.create(
        model=settings.deepseek_model,
        messages=messages,
        max_tokens=effective_max_tokens,
        response_format={"type": "json_object"},
    )

    content = response.choices[0].message.content
    if content is None:
        raise RuntimeError("DeepSeek devolvió una respuesta vacía")

    try:
        data = _parse_json_content(content)
        return LLMPreparationResult.model_validate(data)
    except (json.JSONDecodeError, ValidationError) as exc:
        raise ValueError(f"Respuesta JSON inválida de DeepSeek: {exc}") from exc
