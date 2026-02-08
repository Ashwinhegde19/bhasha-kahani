from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
from uuid import UUID

from app.database import get_db
from app.models.story import Story, StoryTranslation, Character, StoryNode, StoryChoice
from app.schemas.story import (
    StoryListResponse,
    StoryDetailResponse,
    StoryResponse,
    StoryNodeResponse,
    CharacterResponse,
    ChoiceResponse,
)
from app.services.cache_service import CacheService

router = APIRouter()
cache_service = CacheService()


@router.get("", response_model=StoryListResponse)
async def list_stories(
    language: Optional[str] = Query("en", description="Language code"),
    age_range: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """List all stories with pagination"""
    # Check cache first
    cache_key = f"stories:list:{language}:{age_range or 'all'}"
    cached = await cache_service.get(cache_key)
    if cached:
        return StoryListResponse(**cached)
    # Subquery for character count per story
    char_count_subq = (
        select(Character.story_id, func.count(Character.id).label("char_count"))
        .group_by(Character.story_id)
        .subquery()
    )

    # Subquery for choice count per story (via StoryNode)
    choice_count_subq = (
        select(StoryNode.story_id, func.count(StoryChoice.id).label("choice_count"))
        .join(StoryChoice, StoryNode.id == StoryChoice.node_id)
        .group_by(StoryNode.story_id)
        .subquery()
    )

    # Get stories with translations and counts
    query = (
        select(
            Story,
            StoryTranslation,
            char_count_subq.c.char_count,
            choice_count_subq.c.choice_count,
        )
        .join(StoryTranslation, Story.id == StoryTranslation.story_id)
        .outerjoin(char_count_subq, Story.id == char_count_subq.c.story_id)
        .outerjoin(choice_count_subq, Story.id == choice_count_subq.c.story_id)
        .where(StoryTranslation.language_code == language, Story.is_active == True)
    )

    if age_range:
        query = query.where(Story.age_range == age_range)

    result = await db.execute(query)
    rows = result.all()

    stories = []
    for story, translation, char_count, choice_count in rows:
        stories.append(
            StoryResponse(
                id=story.id,
                slug=story.slug,
                title=translation.title,
                description=translation.description or "",
                language=language,
                age_range=story.age_range,
                region=story.region,
                moral=story.moral,
                duration_min=story.duration_min or 0,
                cover_image=story.cover_image or "",
                character_count=char_count or 0,
                choice_count=choice_count or 0,
                is_completed_translation=translation.is_complete,
                created_at=story.created_at,
            )
        )

    response = StoryListResponse(
        data=stories,
        pagination={
            "page": 1,
            "limit": len(stories),
            "total": len(stories),
            "total_pages": 1,
            "has_next": False,
            "has_prev": False,
        },
    )

    # Cache for 10 minutes
    await cache_service.set(cache_key, response.model_dump(mode="json"), ttl=600)

    return response


@router.get("/{slug}", response_model=StoryDetailResponse)
async def get_story(
    slug: str,
    language: Optional[str] = Query("en", description="Language code"),
    db: AsyncSession = Depends(get_db),
):
    """Get story details with nodes and choices"""
    # Check cache first
    cache_key = f"stories:detail:{slug}:{language}"
    cached = await cache_service.get(cache_key)
    if cached:
        return StoryDetailResponse(**cached)

    # Get story
    result = await db.execute(
        select(Story).where(Story.slug == slug, Story.is_active == True)
    )
    story = result.scalar_one_or_none()

    if not story:
        raise HTTPException(status_code=404, detail="Story not found")

    # Get translation
    result = await db.execute(
        select(StoryTranslation).where(
            StoryTranslation.story_id == story.id,
            StoryTranslation.language_code == language,
        )
    )
    translation = result.scalar_one_or_none()

    if not translation:
        # Fallback to English
        result = await db.execute(
            select(StoryTranslation).where(
                StoryTranslation.story_id == story.id,
                StoryTranslation.language_code == "en",
            )
        )
        translation = result.scalar_one_or_none()

    # Get characters directly
    result = await db.execute(select(Character).where(Character.story_id == story.id))
    char_rows = result.scalars().all()

    characters = []
    for char in char_rows:
        # Use translated name if available, fallback to DB name
        translated_name = char.name
        if char.name_translations and isinstance(char.name_translations, dict):
            translated_name = char.name_translations.get(
                language, char.name_translations.get("en", char.name)
            )

        characters.append(
            CharacterResponse(
                id=char.id,
                slug=char.slug,
                name=translated_name,
                voice_profile=char.voice_profile,
                bulbul_speaker=char.bulbul_speaker,
                avatar_url=char.avatar_url,
            )
        )

    # Get nodes directly
    result = await db.execute(select(StoryNode).where(StoryNode.story_id == story.id))
    node_rows = result.scalars().all()

    # Get ALL choices for this story in one query (avoid N+1)
    node_ids = [node.id for node in node_rows]
    choices_by_node = {}
    if node_ids:
        result = await db.execute(
            select(StoryChoice).where(StoryChoice.node_id.in_(node_ids))
        )
        for choice in result.scalars().all():
            choices_by_node.setdefault(choice.node_id, []).append(choice)

    nodes = []
    start_node_id = None

    for node in sorted(node_rows, key=lambda x: x.display_order):
        if node.is_start:
            start_node_id = node.id

        # Get text for current language
        text_content = node.text_content.get(language, node.text_content.get("en", ""))

        # Get character for this node
        character = None
        if node.character_id:
            for char in characters:
                if str(char.id) == str(node.character_id):
                    character = char
                    break

        # Get choices from pre-fetched map
        choices = None
        choice_rows = choices_by_node.get(node.id, [])
        if node.node_type == "choice" and choice_rows:
            choices = []
            for choice in choice_rows:
                choice_text = choice.text_content.get(
                    language, choice.text_content.get("en", "")
                )
                choices.append(
                    ChoiceResponse(
                        id=choice.id,
                        choice_key=choice.choice_key,
                        text=choice_text,
                        next_node_id=choice.next_node_id,
                    )
                )

        nodes.append(
            StoryNodeResponse(
                id=node.id,
                node_type=node.node_type,
                display_order=node.display_order,
                is_start=node.is_start,
                is_end=node.is_end,
                text=text_content,
                character=character,
                choices=choices,
            )
        )

    response = StoryDetailResponse(
        id=story.id,
        slug=story.slug,
        title=translation.title if translation else story.slug,
        description=translation.description if translation else "",
        language=language,
        age_range=story.age_range,
        region=story.region,
        moral=story.moral,
        duration_min=story.duration_min or 0,
        cover_image=story.cover_image or "",
        available_languages=["en", "hi", "kn"],
        characters=characters,
        nodes=nodes,
        start_node_id=start_node_id,
        created_at=story.created_at,
        updated_at=story.updated_at,
    )

    # Cache for 10 minutes
    await cache_service.set(cache_key, response.model_dump(mode="json"), ttl=600)

    return response
