import json
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path
from typing import Any, Optional
from uuid import NAMESPACE_URL, UUID, uuid5

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.exc import SQLAlchemyError

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


def stable_uuid(*parts: str) -> UUID:
    return uuid5(NAMESPACE_URL, ":".join(parts))


def select_translation(
    translations: dict[str, Any], requested_language: str
) -> tuple[Optional[str], Optional[dict[str, Any]]]:
    if not translations:
        return None, None

    if requested_language in translations:
        return requested_language, translations[requested_language]
    if "en" in translations:
        return "en", translations["en"]

    first_language = sorted(translations.keys())[0]
    return first_language, translations[first_language]


@lru_cache(maxsize=1)
def load_fallback_stories() -> list[dict[str, Any]]:
    scripts_dir = Path(__file__).resolve().parents[2] / "scripts"
    stories: list[dict[str, Any]] = []
    for json_path in sorted(scripts_dir.glob("story_*.json")):
        try:
            with json_path.open("r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict):
                stories.append(data)
        except Exception:
            continue
    return stories


def build_story_list_from_fallback(
    requested_language: str, age_range: Optional[str]
) -> StoryListResponse:
    requested_range = parse_age_range(age_range)
    now = datetime.now(timezone.utc)
    data: list[StoryResponse] = []

    for story in load_fallback_stories():
        story_age_range = story.get("age_range", "")
        if age_range:
            story_range = parse_age_range(story_age_range)
            if requested_range and story_range:
                if not ranges_overlap(requested_range, story_range):
                    continue
            elif story_age_range != age_range:
                continue

        translations = story.get("translations")
        if not isinstance(translations, dict):
            continue

        selected_language, selected_translation = select_translation(
            translations, requested_language
        )
        if not selected_translation:
            continue

        raw_nodes = story.get("nodes")
        nodes = raw_nodes if isinstance(raw_nodes, list) else []
        choices_count = 0
        for node in nodes:
            if isinstance(node, dict) and isinstance(node.get("choices"), list):
                choices_count += len(node["choices"])

        slug = str(story.get("slug", "")).strip()
        if not slug:
            continue

        data.append(
            StoryResponse(
                id=stable_uuid("fallback", "story", slug),
                slug=slug,
                title=str(selected_translation.get("title", slug)),
                description=str(selected_translation.get("description", "")),
                language=selected_language or requested_language,
                age_range=story_age_range or "all",
                region=str(story.get("region", "unknown")),
                moral=story.get("moral"),
                duration_min=int(story.get("duration_min", 0) or 0),
                cover_image=str(story.get("cover_image", "")),
                character_count=len(story.get("characters", [])),
                choice_count=choices_count,
                is_completed_translation=True,
                created_at=now,
            )
        )

    response = StoryListResponse(
        data=data,
        pagination={
            "page": 1,
            "limit": len(data),
            "total": len(data),
            "total_pages": 1,
            "has_next": False,
            "has_prev": False,
        },
    )
    return response


def build_story_detail_from_fallback(
    slug: str, requested_language: str
) -> Optional[StoryDetailResponse]:
    match = None
    for story in load_fallback_stories():
        if str(story.get("slug", "")).strip() == slug:
            match = story
            break

    if match is None:
        return None

    translations = match.get("translations")
    if not isinstance(translations, dict):
        return None

    selected_language, selected_translation = select_translation(
        translations, requested_language
    )
    if not selected_translation:
        return None

    character_map: dict[str, CharacterResponse] = {}
    characters: list[CharacterResponse] = []
    for char in match.get("characters", []):
        if not isinstance(char, dict):
            continue
        char_slug = str(char.get("slug", "")).strip()
        if not char_slug:
            continue
        char_id = stable_uuid("fallback", "story", slug, "character", char_slug)
        response = CharacterResponse(
            id=char_id,
            slug=char_slug,
            name=str(char.get("name", char_slug)),
            voice_profile=str(char.get("voice_profile", "narrator")),
            bulbul_speaker=str(char.get("bulbul_speaker", "meera")),
            avatar_url=char.get("avatar_url"),
        )
        characters.append(response)
        character_map[char_slug] = response

    raw_nodes = match.get("nodes")
    nodes_data = raw_nodes if isinstance(raw_nodes, list) else []
    sorted_nodes = sorted(
        [n for n in nodes_data if isinstance(n, dict)],
        key=lambda x: int(x.get("display_order", 0) or 0),
    )
    if not sorted_nodes:
        return None

    node_id_by_order: dict[int, UUID] = {}
    for node in sorted_nodes:
        order = int(node.get("display_order", 0) or 0)
        node_id_by_order[order] = stable_uuid("fallback", "story", slug, "node", str(order))

    nodes: list[StoryNodeResponse] = []
    start_node_id: Optional[UUID] = None
    for node in sorted_nodes:
        order = int(node.get("display_order", 0) or 0)
        node_id = node_id_by_order[order]
        if bool(node.get("is_start")):
            start_node_id = node_id

        choice_responses: Optional[list[ChoiceResponse]] = None
        raw_choices = node.get("choices")
        if node.get("node_type") == "choice" and isinstance(raw_choices, list):
            choice_responses = []
            for idx, choice in enumerate(raw_choices):
                if not isinstance(choice, dict):
                    continue
                choice_key = str(choice.get("choice_key", f"C{idx+1}"))
                next_order = choice.get("next_node_order")
                next_node_id = (
                    node_id_by_order.get(int(next_order))
                    if isinstance(next_order, int)
                    else None
                )
                choice_responses.append(
                    ChoiceResponse(
                        id=stable_uuid(
                            "fallback",
                            "story",
                            slug,
                            "node",
                            str(order),
                            "choice",
                            choice_key,
                        ),
                        choice_key=choice_key,
                        text=get_localized_text(choice.get("text"), selected_language or "en"),
                        next_node_id=next_node_id,
                    )
                )

        nodes.append(
            StoryNodeResponse(
                id=node_id,
                node_type=str(node.get("node_type", "narration")),
                display_order=order,
                is_start=bool(node.get("is_start")),
                is_end=bool(node.get("is_end")),
                text=get_localized_text(node.get("text"), selected_language or "en"),
                character=character_map.get(str(node.get("character_slug", ""))),
                choices=choice_responses,
            )
        )

    if start_node_id is None:
        start_node_id = nodes[0].id

    now = datetime.now(timezone.utc)
    return StoryDetailResponse(
        id=stable_uuid("fallback", "story", slug),
        slug=slug,
        title=str(selected_translation.get("title", slug)),
        description=str(selected_translation.get("description", "")),
        language=selected_language or requested_language,
        age_range=str(match.get("age_range", "all")),
        region=str(match.get("region", "unknown")),
        moral=match.get("moral"),
        duration_min=int(match.get("duration_min", 0) or 0),
        cover_image=str(match.get("cover_image", "")),
        available_languages=sorted(translations.keys()),
        characters=characters,
        nodes=nodes,
        start_node_id=start_node_id,
        created_at=now,
        updated_at=now,
    )


async def execute_with_db_guard(db: AsyncSession, statement):
    try:
        return await db.execute(statement)
    except (SQLAlchemyError, OSError) as exc:
        raise HTTPException(
            status_code=503, detail="Database unavailable. Please try again."
        ) from exc


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
    try:
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

        result = await execute_with_db_guard(db, query)
        rows = result.all()
        requested_range = parse_age_range(age_range)
        story_ids = [story.id for story, _, _ in rows]

        translations_by_story = {}
        if story_ids:
            translation_result = await execute_with_db_guard(
                db,
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
    except HTTPException as exc:
        if exc.status_code != 503:
            raise
        response = build_story_list_from_fallback(requested_language, age_range)

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

    try:
        # Get story
        result = await execute_with_db_guard(
            db,
            select(Story).where(Story.slug == slug, Story.is_active == True)
        )
        story = result.scalar_one_or_none()

        if not story:
            raise HTTPException(status_code=404, detail="Story not found")

        # Get all translations once (for fallback + available languages)
        result = await execute_with_db_guard(
            db,
            select(StoryTranslation).where(StoryTranslation.story_id == story.id)
        )
        translations = result.scalars().all()
        translations_by_lang = {t.language_code: t for t in translations}
        translation = (
            translations_by_lang.get(requested_language)
            or translations_by_lang.get("en")
            or (translations[0] if translations else None)
        )
        selected_language = (
            translation.language_code if translation else requested_language
        )
        available_languages = sorted(translations_by_lang.keys()) or ["en"]

        if not translation:
            raise HTTPException(status_code=404, detail="Story translation not found")

        # Get characters directly
        result = await execute_with_db_guard(
            db, select(Character).where(Character.story_id == story.id)
        )
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
        result = await execute_with_db_guard(
            db, select(StoryNode).where(StoryNode.story_id == story.id)
        )
        node_rows = result.scalars().all()

        # Get ALL choices for this story in one query (avoid N+1)
        node_ids = [node.id for node in node_rows]
        choices_by_node = {}
        if node_ids:
            result = await execute_with_db_guard(
                db,
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
                    choice_text = get_localized_text(
                        choice.text_content, selected_language
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
    except HTTPException as exc:
        if exc.status_code != 503:
            raise
        fallback_response = build_story_detail_from_fallback(slug, requested_language)
        if fallback_response is None:
            raise HTTPException(status_code=404, detail="Story not found") from exc
        response = fallback_response

    # Cache for 10 minutes
    await cache_service.set(cache_key, response.model_dump(mode="json"), ttl=600)

    return response
