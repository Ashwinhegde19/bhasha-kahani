from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://postgres:postgres@localhost:5432/bhashakahani"

    # Redis
    redis_url: str = "redis://localhost:6379"

    # Cloudflare R2 (optional - can use Supabase instead)
    r2_account_id: str = ""
    r2_access_key_id: str = ""
    r2_secret_access_key: str = ""
    r2_bucket_name: str = "bhashakahani-audio"
    r2_public_url: str = ""

    # Supabase Storage (FREE alternative - no credit card needed!)
    supabase_service_key: str = (
        ""  # Get from Supabase Dashboard > Project Settings > API
    )

    # Sarvam Bulbul
    sarvam_api_key: str = ""
    sarvam_base_url: str = "https://api.sarvam.ai"

    # Security
    secret_key: str = "your-super-secret-key-change-this-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24  # 24 hours

    # Audio
    audio_cache_ttl_days: int = 30

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
