"""
Clear audio cache and regenerate audio with correct character voices.
Run this to fix mismatched voice/character issues.
"""

import asyncio
import sys
import os

# Add parent to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import AsyncSessionLocal
from app.models.audio import AudioFile
from app.models.story import StoryNode, Story, Character
from app.services.bulbul_service import BulbulService
from app.services.r2_service import R2Service
from app.services.cache_service import CacheService
from app.config import get_settings

settings = get_settings()
bulbul_service = BulbulService()
cache_service = CacheService()
r2_service = R2Service()


async def clear_all_audio():
    """Clear all audio files from database and cache"""
    async with AsyncSessionLocal() as db:
        # Delete all audio files
        result = await db.execute(delete(AudioFile))
        await db.commit()
        print(f"Deleted {result.rowcount} audio files from database")

        # Clear Redis cache
        try:
            r = await cache_service.connect()
            await r.flushdb()
            print("Cleared Redis cache")
        except Exception as e:
            print(f"Warning: Could not clear Redis cache: {e}")


async def regenerate_story_audio(story_slug: str, language: str = "en"):
    """Regenerate audio for a specific story"""
    async with AsyncSessionLocal() as db:
        # Get story with translations
        from sqlalchemy.orm import joinedload

        result = await db.execute(
            select(Story)
            .options(joinedload(Story.translations))
            .where(Story.slug == story_slug)
        )
        story = result.unique().scalar_one_or_none()

        if not story:
            print(f"Story {story_slug} not found")
            return

        # Get title from translations
        title = story_slug
        for trans in story.translations:
            if trans.language_code == language:
                title = trans.title
                break

        print(f"Regenerating audio for {title} ({language})")

        # Get all narration nodes with character data
        from sqlalchemy.orm import joinedload

        nodes_result = await db.execute(
            select(StoryNode)
            .options(joinedload(StoryNode.character))
            .where(StoryNode.story_id == story.id)
            .where(StoryNode.node_type == "narration")
            .order_by(StoryNode.display_order)
        )
        nodes = nodes_result.scalars().all()

        print(f"Found {len(nodes)} narration nodes")

        for i, node in enumerate(nodes):
            # Get the correct speaker based on character
            speaker = "meera"  # default
            character_name = "Narrator"

            if node.character:
                character_name = node.character.name
                # Use bulbul_speaker from character, or map from character name
                if node.character.bulbul_speaker:
                    speaker = node.character.bulbul_speaker
                else:
                    # Map from character name
                    speaker = bulbul_service.get_speaker_for_character(character_name)

            text = node.text_content.get(language, node.text_content.get("en", ""))
            if not text:
                print(f"  Node {i + 1}: No text, skipping")
                continue

            print(f"  Node {i + 1}: {character_name} -> {speaker} ({len(text)} chars)")

            # Generate audio
            audio_bytes = await bulbul_service.synthesize(text, language, speaker)

            if audio_bytes:
                # Upload to R2
                audio_url = await r2_service.upload_audio(
                    audio_bytes=audio_bytes,
                    story_slug=str(story.slug),
                    node_id=str(node.id),
                    language=language,
                    speaker=speaker,
                )

                # Save to database
                audio_file = AudioFile(
                    node_id=node.id,
                    language_code=language,
                    speaker_id=speaker,
                    r2_url=audio_url,
                    file_size=len(audio_bytes),
                )
                db.add(audio_file)
                await db.flush()

                # Cache
                await cache_service.set_audio_url(
                    str(node.id), language, speaker, audio_url
                )
                print(f"    ✓ Generated and saved")
            else:
                print(f"    ✗ Failed to generate")

        await db.commit()
        print(f"Done! Regenerated audio for {title}")


async def main():
    import argparse

    parser = argparse.ArgumentParser(description="Clear and regenerate story audio")
    parser.add_argument(
        "--clear-only", action="store_true", help="Only clear audio, don't regenerate"
    )
    parser.add_argument("--story", default="punyakoti", help="Story slug to regenerate")
    parser.add_argument("--language", default="en", help="Language code (en, hi, kn)")
    args = parser.parse_args()

    print("Clearing all existing audio...")
    await clear_all_audio()

    if not args.clear_only:
        print(f"\nRegenerating audio for {args.story}...")
        await regenerate_story_audio(args.story, args.language)

    print("\nDone!")


if __name__ == "__main__":
    asyncio.run(main())
