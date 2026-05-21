from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    deepseek_api_key: str
    deepseek_model: str
    deepseek_base_url: str = "https://api.deepseek.com"
    deepseek_max_tokens: int = 8192

    max_upload_bytes: int = 10 * 1024 * 1024
    max_chars_per_segment: int = 30000
    segment_overlap_chars: int = 500

    embedding_model: str = (
        "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    )

    cors_origins: str = "http://localhost:5173"

    @property
    def cors_origins_list(self) -> list[str]:
        origins = [
            origin.strip().rstrip("/")
            for origin in self.cors_origins.split(",")
            if origin.strip()
        ]
        return origins or ["http://localhost:5173"]


@lru_cache
def get_settings() -> Settings:
    return Settings()
