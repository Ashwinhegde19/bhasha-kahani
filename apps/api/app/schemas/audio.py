from uuid import UUID
from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class AudioResponse(BaseModel):
    node_id: UUID
    language: str
    code_mix_ratio: float
    speaker: str
    audio_url: str
    duration_sec: Optional[float] = None
    file_size: Optional[int] = None
    is_cached: bool = True
    expires_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class AudioGeneratingResponse(BaseModel):
    node_id: UUID
    language: str
    status: str = "generating"
    estimated_wait_sec: int = 5
    retry_after: int = 5
