"""
Seed script to add stories to the database.
Usage: python scripts/seed_stories.py
"""
import asyncio
import json
import sys
from pathlib import Path
from uuid import uuid4

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import AsyncSession
from app.database import AsyncSessionLocal, engine
from app.models import Base, Story, StoryTranslation, Character, StoryNode, StoryChoice


async def seed_database():
    """Seed database with stories"""
    async with AsyncSessionLocal() as db:
        # Load story data
        stories_dir = Path(__file__).parent
        
        story_files = [
            stories_dir / "story_clever_crow.json",
            stories_dir / "story_punyakoti.json"
        ]
        
        for story_file in story_files:
            if not story_file.exists():
                print(f"⚠️  File not found: {story_file}")
                continue
            
            with open(story_file) as f:
                data = json.load(f)
            
            # Check if story already exists
            from sqlalchemy import select
            result = await db.execute(
                select(Story).where(Story.slug == data["slug"])
            )
            if result.scalar_one_or_none():
                print(f"✅ Story '{data['slug']}' already exists, skipping")
                continue
            
            print(f"📝 Adding story: {data['slug']}")
            
            # Create story
            story = Story(
                slug=data["slug"],
                age_range=data["age_range"],
                region=data["region"],
                moral=data["moral"],
                duration_min=data["duration_min"],
                cover_image=data["cover_image"],
                is_active=True
            )
            db.add(story)
            await db.flush()
            
            # Add translations
            for lang_code, trans in data["translations"].items():
                translation = StoryTranslation(
                    story_id=story.id,
                    language_code=lang_code,
                    title=trans["title"],
                    description=trans["description"],
                    content_json={},
                    is_complete=True
                )
                db.add(translation)
            
            # Add characters
            characters = {}
            for char_data in data["characters"]:
                char = Character(
                    story_id=story.id,
                    slug=char_data["slug"],
                    name=char_data["name"],
                    voice_profile=char_data["voice_profile"],
                    bulbul_speaker=char_data["bulbul_speaker"],
                    avatar_url=char_data.get("avatar_url")
                )
                db.add(char)
                await db.flush()
                characters[char_data["slug"]] = char.id
            
            # Add nodes
            nodes = {}
            for node_data in data["nodes"]:
                node = StoryNode(
                    story_id=story.id,
                    node_type=node_data["node_type"],
                    character_id=characters.get(node_data.get("character_slug")),
                    display_order=node_data["display_order"],
                    is_start=node_data["is_start"],
                    is_end=node_data["is_end"],
                    text_content=node_data["text"],
                    node_metadata={}
                )
                db.add(node)
                await db.flush()
                nodes[node_data["display_order"]] = node
            
            # Add choices
            for node_data in data["nodes"]:
                if node_data.get("choices"):
                    current_node = nodes[node_data["display_order"]]
                    for choice_data in node_data["choices"]:
                        next_node = nodes.get(choice_data["next_node_order"])
                        choice = StoryChoice(
                            node_id=current_node.id,
                            choice_key=choice_data["choice_key"],
                            text_content=choice_data["text"],
                            next_node_id=next_node.id if next_node else None
                        )
                        db.add(choice)
            
            print(f"✅ Story '{data['slug']}' added successfully!")
        
        await db.commit()
        print("🎉 All stories seeded successfully!")


if __name__ == "__main__":
    asyncio.run(seed_database())
