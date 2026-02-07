from typing import Optional, List, Dict, Any
from uuid import UUID
from pydantic import BaseModel
from datetime import datetime


class CharacterBase(BaseModel):
    slug: str
    name: str
    voice_profile: str
    bulbul_speaker: str
    avatar_url: Optional[str] = None


class CharacterResponse(CharacterBase):
    id: UUID
    
    class Config:
        from_attributes = True


class ChoiceBase(BaseModel):
    choice_key: str
    text: str
    next_node_id: Optional[UUID] = None


class ChoiceResponse(ChoiceBase):
    id: UUID
    
    class Config:
        from_attributes = True


class StoryNodeBase(BaseModel):
    id: UUID
    node_type: str  # narration, dialogue, choice, end
    display_order: int
    is_start: bool
    is_end: bool
    text: str
    character: Optional[CharacterResponse] = None
    choices: Optional[List[ChoiceResponse]] = None


class StoryNodeResponse(StoryNodeBase):
    class Config:
        from_attributes = True


class StoryBase(BaseModel):
    slug: str
    title: str
    description: str
    language: str
    age_range: str
    region: str
    moral: Optional[str] = None
    duration_min: int
    cover_image: str


class StoryCreate(StoryBase):
    pass


class StoryResponse(StoryBase):
    id: UUID
    character_count: int = 0
    choice_count: int = 0
    is_completed_translation: bool = True
    created_at: datetime
    
    class Config:
        from_attributes = True


class StoryListResponse(BaseModel):
    data: List[StoryResponse]
    pagination: Dict[str, Any]


class StoryDetailResponse(StoryBase):
    id: UUID
    available_languages: List[str]
    characters: List[CharacterResponse]
    nodes: List[StoryNodeResponse]
    start_node_id: UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class MakeChoiceRequest(BaseModel):
    node_id: UUID
    choice_key: str


class MakeChoiceResponse(BaseModel):
    success: bool
    choice_made: Dict[str, Any]
    next_node: StoryNodeResponse
    progress: Dict[str, Any]
