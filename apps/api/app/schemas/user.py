from uuid import UUID
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any


class UserBase(BaseModel):
    anonymous_id: str
    preferences: Optional[Dict[str, Any]] = {}


class UserCreate(UserBase):
    pass


class UserResponse(UserBase):
    id: UUID
    created_at: datetime
    last_active: datetime
    
    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user_id: UUID
