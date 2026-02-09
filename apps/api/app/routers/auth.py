from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
import jwt
from uuid import uuid4

from app.database import get_db
from app.models.user import User
from app.schemas.user import TokenResponse
from app.config import get_settings

settings = get_settings()
router = APIRouter()


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.access_token_expire_minutes
        )

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.secret_key, algorithm=settings.algorithm
    )
    return encoded_jwt, expire


@router.post("/anonymous", response_model=TokenResponse)
async def create_anonymous_user(db: AsyncSession = Depends(get_db)):
    """Create anonymous user and return JWT token"""
    # Generate unique anonymous ID
    anonymous_id = f"anon_{uuid4().hex[:16]}"

    # Create user
    user = User(
        anonymous_id=anonymous_id, preferences={"language": "en", "code_mix_ratio": 0.0}
    )
    db.add(user)
    await db.flush()

    # Create access token
    access_token, _ = create_access_token(
        data={"sub": str(user.id), "anonymous_id": anonymous_id}
    )

    return TokenResponse(
        access_token=access_token,
        expires_in=int(settings.access_token_expire_minutes * 60),
        user_id=user.id,
    )
