from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional

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


def translation_priority(language_code: str, requested_language: str) -> int:
    if language_code == requested_language:
        return 0
    if language_code == "en":
        return 1
    return 2


def parse_age_range(value: Optional[str]) -> Optional[tuple[int, int]]:
    if not value or "-" not in value:
        return None
    low, high = value.split("-", 1)
    try:
        low_i = int(low.strip())
        high_i = int(high.strip())
        if low_i > high_i:
            low_i, high_i = high_i, low_i
        return low_i, high_i
    except ValueError:
        return None


def ranges_overlap(a: tuple[int, int], b: tuple[int, int]) -> bool:
    return a[0] <= b[1] and b[0] <= a[1]


def get_localized_text(content: Optional[dict], language: str) -> str:
    if not isinstance(content, dict):
        return ""
    return content.get(language, content.get("en", ""))


@router.get("", response_model=StoryListResponse)
async def list_stories(
    language: Optional[str] = Query("en", description="Language code"),
    age_range: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """List all stories with pagination"""
    requested_language = (language or "en").strip().lower()

    # Check cache first
    cache_key = f"stories:v2:list:{requested_language}:{age_range or 'all'}"
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

    # Get active stories with counts
    query = (
        select(
            Story,
            char_count_subq.c.char_count,
            choice_count_subq.c.choice_count,
        )
        .outerjoin(char_count_subq, Story.id == char_count_subq.c.story_id)
        .outerjoin(choice_count_subq, Story.id == choice_count_subq.c.story_id)
        .where(Story.is_active == True)
    )

    result = await db.execute(query)
    rows = result.all()
    requested_range = parse_age_range(age_range)
    story_ids = [story.id for story, _, _ in rows]

    translations_by_story = {}
    if story_ids:
        translation_result = await db.execute(
            select(StoryTranslation).where(
                StoryTranslation.story_id.in_(story_ids),
            )
        )
        for translation in translation_result.scalars().all():
            existing = translations_by_story.get(translation.story_id)
            if existing is None:
                translations_by_story[translation.story_id] = translation
                continue

            if translation_priority(
                translation.language_code, requested_language
            ) < translation_priority(existing.language_code, requested_language):
                translations_by_story[translation.story_id] = translation

    stories = []
    for story, char_count, choice_count in rows:
        if age_range:
            story_range = parse_age_range(story.age_range)
            if requested_range and story_range:
                if not ranges_overlap(requested_range, story_range):
                    continue
            elif story.age_range != age_range:
                continue

        translation = translations_by_story.get(story.id)
        if not translation:
            continue

        stories.append(
            StoryResponse(
                id=story.id,
                slug=story.slug,
                title=translation.title,
                description=translation.description or "",
                language=translation.language_code,
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
    requested_language = (language or "en").strip().lower()

    # Check cache first
    cache_key = f"stories:v2:detail:{slug}:{requested_language}"
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

    # Get all translations once (for fallback + available languages)
    result = await db.execute(
        select(StoryTranslation).where(StoryTranslation.story_id == story.id)
    )
    translations = result.scalars().all()
    translations_by_lang = {t.language_code: t for t in translations}
    translation = (
        translations_by_lang.get(requested_language)
        or translations_by_lang.get("en")
        or (translations[0] if translations else None)
    )
    selected_language = translation.language_code if translation else requested_language
    available_languages = sorted(translations_by_lang.keys()) or ["en"]

    if not translation:
        raise HTTPException(status_code=404, detail="Story translation not found")

    # Get characters directly
    result = await db.execute(select(Character).where(Character.story_id == story.id))
    char_rows = result.scalars().all()

    characters = []
    for char in char_rows:
        # Use translated name if available, fallback to DB name
        translated_name = char.name
        if char.name_translations and isinstance(char.name_translations, dict):
            translated_name = char.name_translations.get(
                selected_language, char.name_translations.get("en", char.name)
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

    sorted_nodes = sorted(node_rows, key=lambda x: x.display_order)
    if not sorted_nodes:
        raise HTTPException(status_code=404, detail="Story has no nodes")

    nodes = []
    start_node_id = None

    for node in sorted_nodes:
        if node.is_start:
            start_node_id = node.id

        # Get text for current language
        text_content = get_localized_text(node.text_content, selected_language)

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
                choice_text = get_localized_text(choice.text_content, selected_language)
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

    if start_node_id is None:
        start_node_id = sorted_nodes[0].id

    response = StoryDetailResponse(
        id=story.id,
        slug=story.slug,
        title=translation.title if translation else story.slug,
        description=translation.description if translation else "",
        language=selected_language,
        age_range=story.age_range,
        region=story.region,
        moral=story.moral,
        duration_min=story.duration_min or 0,
        cover_image=story.cover_image or "",
        available_languages=available_languages,
        characters=characters,
        nodes=nodes,
        start_node_id=start_node_id,
        created_at=story.created_at,
        updated_at=story.updated_at,
    )

    # Cache for 10 minutes
    await cache_service.set(cache_key, response.model_dump(mode="json"), ttl=600)

    return response
