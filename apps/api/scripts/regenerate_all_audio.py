#!/usr/bin/env python3
"""Regenerate all audio for a story with all speakers"""

import asyncio
import redis.asyncio as redis
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import select, delete
import sys

sys.path.insert(0, "/home/ashwin/Projects/bhasha-kahani/apps/api")

from app.config import get_settings
from app.models.audio import AudioFile
from app.models.story import StoryNode
from app.services.bulbul_service import BulbulService

SPEAKERS = [
    "ajji",
    "punyakoti",
    "arbhuta",
    "meera",
    "pooja",
    "neha",
    "aditya",
    "arvind",
]
LANGUAGES = ["en", "hi", "kn"]


async def regenerate_all_audio(story_id: str):
    settings = get_settings()

    redis_client = redis.from_url(settings.redis_url, decode_responses=True)
    engine = create_async_engine(
        settings.database_url.replace("postgresql://", "postgresql+asyncpg://")
    )

    bulbul = BulbulService()

    async with engine.begin() as conn:
        # Get all narration nodes
        result = await conn.execute(
            select(StoryNode)
            .where(StoryNode.story_id == story_id)
            .where(StoryNode.node_type == "narration")
            .order_by(StoryNode.display_order)
        )
        nodes = result.scalars().all()

        print(f"Found {len(nodes)} narration nodes")

        # Clear cache and generate for each node + speaker + language
        count = 0
        for node in nodes:
            for lang in LANGUAGES:
                for speaker in SPEAKERS:
                    # Clear Redis (key format must match cache_service: node:lang:speaker:code_mix)
                    key = f"audio:{node.id}:{lang}:{speaker}:0.00"
                    await redis_client.delete(key)

                    # Get text
                    text = node.text_content.get(lang, node.text_content.get("en", ""))
                    if not text:
                        continue

                    # Generate audio
                    print(f"Generating: {speaker} ({lang}) - {len(text)} chars")
                    audio_bytes = await bulbul.synthesize(text, lang, speaker)
                    if audio_bytes:
                        count += 1
                        print(f"  ✓ Generated for {node.id[:8]}...")
                    else:
                        print(f"  ✗ Failed for {node.id[:8]}")

    await redis_client.aclose()
    await engine.dispose()
    print(f"\n✅ Generated {count} audio files")


if __name__ == "__main__":
    story_id = "96603cb7-cb25-4466-9e4c-ce929283063d"  # Punyakoti
    asyncio.run(regenerate_all_audio(story_id))
