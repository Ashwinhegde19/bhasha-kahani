from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
import uuid as uuid_module
from typing import Union

from app.database import get_db
from app.models.audio import AudioFile
from app.models.story import StoryNode, Story
from app.schemas.audio import AudioResponse, AudioGeneratingResponse
from app.services.bulbul_service import BulbulService
from app.services.cache_service import CacheService
from app.services.r2_service import R2Service

router = APIRouter()
bulbul_service = BulbulService()
cache_service = CacheService()
r2_service = R2Service()


@router.get("/{node_id}", response_model=Union[AudioResponse, AudioGeneratingResponse])
async def get_audio(
    node_id: UUID,
    language: str = Query(..., description="Language code: en, hi, kn"),
    speaker: str = Query("meera", description="Speaker voice"),
    code_mix: float = Query(0.0, ge=0.0, le=1.0),
    db: AsyncSession = Depends(get_db),
):
    """Get audio URL for a story node"""

    # Check cache first
    cached_url = await cache_service.get_audio_url(str(node_id), language, speaker)
    if cached_url:
        return AudioResponse(
            node_id=node_id,
            language=language,
            code_mix_ratio=code_mix,
            speaker=speaker,
            audio_url=cached_url,
            is_cached=True,
        )

    # Check database
    result = await db.execute(
        select(AudioFile).where(
            AudioFile.node_id == node_id,
            AudioFile.language_code == language,
            AudioFile.speaker_id == speaker,
        )
    )
    audio_file = result.scalar_one_or_none()

    if audio_file:
        # Cache and return
        await cache_service.set_audio_url(
            str(node_id), language, speaker, audio_file.r2_url
        )
        return AudioResponse(
            node_id=node_id,
            language=language,
            code_mix_ratio=code_mix,
            speaker=speaker,
            audio_url=audio_file.r2_url,
            duration_sec=float(audio_file.duration_sec)
            if audio_file.duration_sec
            else None,
            file_size=audio_file.file_size,
            is_cached=True,
        )

    # Get node text
    result = await db.execute(select(StoryNode).where(StoryNode.id == node_id))
    node = result.scalar_one_or_none()

    if not node:
        raise HTTPException(status_code=404, detail="Node not found")

    text = node.text_content.get(language, node.text_content.get("en", ""))

    if not text:
        raise HTTPException(status_code=404, detail="Text not found for language")

    # Generate audio on-the-fly
    audio_bytes = await bulbul_service.synthesize(text, language, speaker, code_mix)

    if not audio_bytes:
        # Return generating status with all required fields
        return AudioGeneratingResponse(
            node_id=node_id,
            language=language,
            code_mix_ratio=code_mix,
            speaker=speaker,
            audio_url="",
            status="generating",
            estimated_wait_sec=5,
            retry_after=5,
        )

    # Get story slug for R2 path
    story_result = await db.execute(select(Story.slug).where(Story.id == node.story_id))
    story_slug = story_result.scalar_one_or_none() or "unknown"

    # Upload to R2
    audio_url = await r2_service.upload_audio(
        audio_bytes=audio_bytes,
        story_slug=story_slug,
        node_id=str(node_id),
        language=language,
        speaker=speaker,
    )

    if not audio_url:
        # Fallback to placeholder if R2 upload fails
        audio_url = f"https://audio.bhashakahani.com/{language}/generated/{uuid_module.uuid4()}.mp3"

    # Save to database
    new_audio = AudioFile(
        node_id=node_id,
        language_code=language,
        code_mix_ratio=code_mix,
        speaker_id=speaker,
        r2_url=audio_url,
        file_size=len(audio_bytes),
    )
    db.add(new_audio)
    await db.flush()

    # Cache
    await cache_service.set_audio_url(str(node_id), language, speaker, audio_url)

    return AudioResponse(
        node_id=node_id,
        language=language,
        code_mix_ratio=code_mix,
        speaker=speaker,
        audio_url=audio_url,
        file_size=len(audio_bytes),
        is_cached=False,
    )
