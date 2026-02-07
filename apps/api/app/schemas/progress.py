from uuid import UUID
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List, Dict, Any


class ProgressCreate(BaseModel):
    story_id: UUID
    current_node_id: Optional[UUID] = None
    is_completed: bool = False
    time_spent_sec: int = 0


class ProgressResponse(BaseModel):
    story_id: UUID
    story_slug: str
    story_title: str
    cover_image: str
    current_node_id: Optional[UUID] = None
    is_completed: bool
    completion_percentage: float
    play_count: int
    total_time_sec: int
    last_played_at: Optional[datetime] = None
    choices_made: List[Dict[str, Any]]
    
    class Config:
        from_attributes = True


class ProgressSummary(BaseModel):
    data: List[ProgressResponse]
    summary: Dict[str, Any]
