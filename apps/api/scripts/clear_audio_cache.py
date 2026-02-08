#!/usr/bin/env python3
"""Clear audio cache and database records for regeneration"""

import asyncio
import redis.asyncio as redis
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import select, delete
import sys

sys.path.insert(0, "/home/ashwin/Projects/bhasha-kahani/apps/api")

from app.config import get_settings
from app.models.audio import AudioFile


async def clear_audio_for_story(story_id: str, language: str = None):
    settings = get_settings()

    # Connect to Redis
    redis_client = redis.from_url(settings.redis_url, decode_responses=True)

    # Connect to database
    engine = create_async_engine(
        settings.database_url.replace("postgresql://", "postgresql+asyncpg://")
    )
    async with engine.begin() as conn:
        # Get audio file IDs for this story
        from app.models.story import StoryNode

        result = await conn.execute(
            select(
                AudioFile.id,
                AudioFile.node_id,
                AudioFile.language_code,
                AudioFile.speaker_id,
            )
            .join(StoryNode, StoryNode.id == AudioFile.node_id)
            .where(StoryNode.story_id == story_id)
        )
        audio_files = result.all()

        print(f"Found {len(audio_files)} audio files for story {story_id}")

        # Delete Redis keys
        keys_deleted = 0
        for audio_file in audio_files:
            key = f"audio:{audio_file.node_id}:{audio_file.language_code}:{audio_file.speaker_id}"
            deleted = await redis_client.delete(key)
            keys_deleted += deleted
            print(f"Deleted Redis key: {key}")

        print(f"Total Redis keys deleted: {keys_deleted}")

        # Delete database records
        if language:
            # Delete for specific language
            result = await conn.execute(
                delete(AudioFile)
                .where(AudioFile.language_code == language)
                .where(
                    AudioFile.node_id.in_(
                        select(StoryNode.id).where(StoryNode.story_id == story_id)
                    )
                )
            )
        else:
            # Delete all audio for story
            result = await conn.execute(
                delete(AudioFile).where(
                    AudioFile.node_id.in_(
                        select(StoryNode.id).where(StoryNode.story_id == story_id)
                    )
                )
            )

        print(f"Deleted {result.rowcount} audio file records from database")

    await redis_client.close()
    await engine.dispose()


if __name__ == "__main__":
    story_id = "96603cb7-cb25-4466-9e4c-ce929283063d"  # Punyakoti
    asyncio.run(clear_audio_for_story(story_id))
    print(
        "\n✅ Audio cache cleared! Next request will generate fresh audio with new settings."
    )
