#!/usr/bin/env python3
"""
Bulk Audio Generation Script for Bhasha Kahani
Generates audio for all stories, all languages, and all speakers
"""

import asyncio
import os
import sys
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.database import AsyncSessionLocal
from app.models.story import Story, StoryNode, Character
from app.models.audio import AudioFile
from app.services.bulbul_service import BulbulService
from app.services.r2_service import R2Service
from app.services.cache_service import CacheService


class BulkAudioGenerator:
    def __init__(self):
        self.bulbul_service = BulbulService()
        self.r2_service = R2Service()
        self.cache_service = CacheService()

    async def generate_all_audio(self, db: AsyncSession):
        """Generate audio for all stories, languages, and speakers"""

        # Get all stories with their characters
        stories_result = await db.execute(select(Story).where(Story.is_active == True))
        stories = stories_result.scalars().all()

        total_generated = 0
        total_skipped = 0
        total_failed = 0

        for story in stories:
            print(f"\n{'=' * 60}")
            print(f"Processing story: {story.slug}")
            print(f"{'=' * 60}")

            # Get all nodes for this story
            nodes_result = await db.execute(
                select(StoryNode).where(StoryNode.story_id == story.id)
            )
            nodes = nodes_result.scalars().all()

            # Get all characters for this story
            chars_result = await db.execute(
                select(Character).where(Character.story_id == story.id)
            )
            characters = chars_result.scalars().all()

            # Create speaker mapping for this story
            speaker_map = {char.id: char.bulbul_speaker for char in characters}
            default_speaker = "pooja"  # Default narrator voice

            # Languages to generate
            languages = ["en", "hi", "kn"]

            for node in nodes:
                # Determine speaker for this node
                speaker = speaker_map.get(node.character_id, default_speaker)

                for language in languages:
                    # Check if audio already exists
                    existing_result = await db.execute(
                        select(AudioFile).where(
                            AudioFile.node_id == node.id,
                            AudioFile.language_code == language,
                            AudioFile.speaker_id == speaker,
                        )
                    )
                    existing = existing_result.scalar_one_or_none()

                    if existing:
                        print(f"  ⏭️  Skipping {language}/{speaker} - already exists")
                        total_skipped += 1
                        continue

                    # Get text for this language
                    text = node.text_content.get(
                        language, node.text_content.get("en", "")
                    )

                    if not text:
                        print(f"  ⚠️  No text for {language}")
                        continue

                    # Generate audio
                    print(f"  🎙️  Generating {language}/{speaker}...", end=" ")
                    try:
                        audio_bytes = await self.bulbul_service.synthesize(
                            text=text, language=language, speaker=speaker
                        )

                        if not audio_bytes:
                            print("FAILED")
                            total_failed += 1
                            continue

                        # Upload to R2
                        audio_url = await self.r2_service.upload_audio(
                            audio_bytes=audio_bytes,
                            story_slug=story.slug,
                            node_id=str(node.id),
                            language=language,
                            speaker=speaker,
                        )

                        if not audio_url:
                            print("R2 UPLOAD FAILED")
                            total_failed += 1
                            continue

                        # Save to database
                        new_audio = AudioFile(
                            node_id=node.id,
                            language_code=language,
                            speaker_id=speaker,
                            r2_url=audio_url,
                            file_size=len(audio_bytes),
                        )
                        db.add(new_audio)
                        await db.flush()

                        # Cache
                        await self.cache_service.set_audio_url(
                            str(node.id), language, speaker, audio_url
                        )

                        print(f"✓ ({len(audio_bytes)} bytes)")
                        total_generated += 1

                    except Exception as e:
                        print(f"ERROR: {e}")
                        total_failed += 1
                        continue

        # Commit all changes
        await db.commit()

        print(f"\n{'=' * 60}")
        print("BULK AUDIO GENERATION COMPLETE")
        print(f"{'=' * 60}")
        print(f"✓ Generated: {total_generated}")
        print(f"⏭️  Skipped: {total_skipped}")
        print(f"✗ Failed: {total_failed}")
        print(f"{'=' * 60}\n")

        return total_generated, total_skipped, total_failed


async def main():
    """Main entry point"""
    print("\n" + "=" * 60)
    print("BHASHA KAHANI - BULK AUDIO GENERATION")
    print("=" * 60 + "\n")

    # Check environment
    from app.config import get_settings

    settings = get_settings()

    if not settings.sarvam_api_key:
        print("❌ SARVAM_API_KEY not configured!")
        print("Set it in your .env file")
        sys.exit(1)

    if not settings.r2_account_id:
        print("⚠️  R2 credentials not configured - audio will not be uploaded to CDN")
        print("Continuing anyway (URLs will be placeholders)...\n")

    async with AsyncSessionLocal() as db:
        generator = BulkAudioGenerator()
        generated, skipped, failed = await generator.generate_all_audio(db)

    if failed > 0:
        sys.exit(1)

    print("✅ All audio generated successfully!\n")


if __name__ == "__main__":
    asyncio.run(main())
