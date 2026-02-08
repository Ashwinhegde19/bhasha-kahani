from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
import uuid as uuid_module
from typing import Union
import io

from app.database import get_db
from app.models.audio import AudioFile
from app.models.story import StoryNode, Story
from app.schemas.audio import AudioResponse, AudioGeneratingResponse
from app.services.bulbul_service import BulbulService
from app.services.cache_service import CacheService
from app.services.r2_service import R2Service
from pydub import AudioSegment

router = APIRouter()
bulbul_service = BulbulService()
cache_service = CacheService()
r2_service = R2Service()


async def generate_story_audio_for_language(
    story_id: UUID, language: str, db: AsyncSession
):
    """Background task to generate full story audio for a specific language"""

    # Get story and nodes
    story_result = await db.execute(select(Story).where(Story.id == story_id))
    story = story_result.scalar_one_or_none()

    if not story:
        return

    # Get all narration nodes in order
    nodes_result = await db.execute(
        select(StoryNode)
        .where(StoryNode.story_id == story_id)
        .where(StoryNode.node_type == "narration")
        .order_by(StoryNode.display_order)
    )
    nodes = nodes_result.scalars().all()

    if not nodes:
        return

    # Generate audio for each node
    audio_segments = []

    for node in nodes:
        speaker = node.speaker if hasattr(node, "speaker") and node.speaker else "meera"

        text = node.text_content.get(language, node.text_content.get("en", ""))
        if not text:
            continue

        audio_bytes = await bulbul_service.synthesize(text, language, speaker)
        if audio_bytes:
            audio_segments.append(audio_bytes)

    if not audio_segments:
        return

    # Concatenate all audio segments using pydub
    combined_audio = AudioSegment.empty()
    for segment_bytes in audio_segments:
        segment = AudioSegment.from_wav(io.BytesIO(segment_bytes))
        combined_audio += segment

    # Export as MP3
    mp3_buffer = io.BytesIO()
    combined_audio.export(mp3_buffer, format="mp3", bitrate="128k")
    full_audio = mp3_buffer.getvalue()

    # Upload combined audio
    await r2_service.upload_audio(
        audio_bytes=full_audio,
        story_slug=str(story.slug),
        node_id="full-story",
        language=language,
        speaker="combined",
    )


@router.post("/story/{story_id}/pre-generate")
async def pre_generate_all_languages(
    story_id: UUID,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """Pre-generate audio for all supported languages in the background"""

    # Get story
    story_result = await db.execute(select(Story).where(Story.id == story_id))
    story = story_result.scalar_one_or_none()

    if not story:
        raise HTTPException(status_code=404, detail="Story not found")

    # Queue background generation for all available languages
    # Get languages from translations
    languages = ["en", "hi", "kn"]  # Default languages
    for language in languages:
        background_tasks.add_task(
            generate_story_audio_for_language, story_id, language, db
        )

    return {
        "story_id": story_id,
        "message": f"Audio generation started for {len(languages)} languages",
        "languages": languages,
        "status": "generating_in_background",
    }


@router.post("/story/{story_id}/full")
async def generate_full_story_audio(
    story_id: UUID,
    language: str = Query(..., description="Language code: en, hi, kn"),
    db: AsyncSession = Depends(get_db),
):
    """Generate full story audio by concatenating all narration nodes"""

    # Get story and nodes
    story_result = await db.execute(select(Story).where(Story.id == story_id))
    story = story_result.scalar_one_or_none()

    if not story:
        raise HTTPException(status_code=404, detail="Story not found")

    # Get all narration nodes in order
    nodes_result = await db.execute(
        select(StoryNode)
        .where(StoryNode.story_id == story_id)
        .where(StoryNode.node_type == "narration")
        .order_by(StoryNode.display_order)
    )
    nodes = nodes_result.scalars().all()

    if not nodes:
        raise HTTPException(status_code=404, detail="No narration nodes found")

    # Generate audio for each node
    audio_segments = []

    for node in nodes:
        speaker = node.speaker if hasattr(node, "speaker") and node.speaker else "meera"

        text = node.text_content.get(language, node.text_content.get("en", ""))
        if not text:
            continue

        audio_bytes = await bulbul_service.synthesize(text, language, speaker)
        if audio_bytes:
            audio_segments.append(audio_bytes)

    if not audio_segments:
        raise HTTPException(
            status_code=500, detail="Failed to generate any audio segments"
        )

    # Concatenate all audio segments using pydub
    combined_audio = AudioSegment.empty()
    for segment_bytes in audio_segments:
        segment = AudioSegment.from_wav(io.BytesIO(segment_bytes))
        combined_audio += segment

    # Export as MP3
    mp3_buffer = io.BytesIO()
    combined_audio.export(mp3_buffer, format="mp3", bitrate="128k")
    full_audio = mp3_buffer.getvalue()

    # Upload combined audio
    combined_url = await r2_service.upload_audio(
        audio_bytes=full_audio,
        story_slug=str(story.slug),
        node_id="full-story",
        language=language,
        speaker="combined",
    )

    return {
        "story_id": story_id,
        "language": language,
        "audio_url": combined_url,
        "total_nodes": len(nodes),
        "total_duration_sec": len(combined_audio) / 1000,
        "file_size": len(full_audio),
    }


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
        story_slug=str(story_slug),
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
