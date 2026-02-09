from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.database import get_db
from app.models.story import Story, StoryNode, StoryChoice, Character
from app.models.progress import UserProgress
from app.schemas.story import (
    MakeChoiceRequest,
    MakeChoiceResponse,
    StoryNodeResponse,
    ChoiceResponse,
    CharacterResponse,
)
from app.utils.auth import get_optional_user_id

router = APIRouter()


def get_localized_text(text_content: Optional[dict], language: str) -> str:
    if not isinstance(text_content, dict):
        return ""
    return text_content.get(language, text_content.get("en", ""))


@router.post("/{slug}/choices", response_model=MakeChoiceResponse)
async def make_choice(
    slug: str,
    request: MakeChoiceRequest,
    user_id: Optional[UUID] = Query(
        None, description="Backward-compatible user id query param"
    ),
    token_user_id: Optional[UUID] = Depends(get_optional_user_id),
    language: str = Query("en", description="Language code"),
    db: AsyncSession = Depends(get_db)
):
    """Make a choice and get next node"""
    resolved_user_id = token_user_id or user_id

    # Get story
    result = await db.execute(
        select(Story).where(Story.slug == slug)
    )
    story = result.scalar_one_or_none()
    
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    
    # Get current node
    result = await db.execute(
        select(StoryNode).where(
            StoryNode.id == request.node_id, StoryNode.story_id == story.id
        )
    )
    current_node = result.scalar_one_or_none()
    
    if not current_node:
        raise HTTPException(status_code=404, detail="Node not found")
    
    # Get the choice
    result = await db.execute(
        select(StoryChoice).where(
            StoryChoice.node_id == request.node_id,
            StoryChoice.choice_key == request.choice_key
        )
    )
    choice = result.scalar_one_or_none()
    
    if not choice:
        raise HTTPException(status_code=400, detail="Invalid choice")
    
    # Get next node
    next_node = None
    if choice.next_node_id:
        result = await db.execute(
            select(StoryNode).where(
                StoryNode.id == choice.next_node_id, StoryNode.story_id == story.id
            )
        )
        next_node = result.scalar_one_or_none()
    
    if not next_node:
        raise HTTPException(status_code=404, detail="Next node not found")
    
    max_order_result = await db.execute(
        select(func.max(StoryNode.display_order)).where(StoryNode.story_id == story.id)
    )
    max_display_order = max_order_result.scalar() or 1
    completion_percentage = min(
        100.0, max(0.0, (next_node.display_order / max_display_order) * 100.0)
    )

    choices_made_count = 1

    # Update user progress if user_id provided
    if resolved_user_id:
        result = await db.execute(
            select(UserProgress).where(
                UserProgress.user_id == resolved_user_id,
                UserProgress.story_id == story.id
            )
        )
        progress = result.scalar_one_or_none()

        if not progress:
            progress = UserProgress(
                user_id=resolved_user_id,
                story_id=story.id,
                current_node_id=next_node.id,
                choices_made=[],
                play_count=1,
                total_time_sec=0,
            )
            db.add(progress)

        # Use a new list instance so SQLAlchemy always detects JSON changes.
        choices_made = list(progress.choices_made or [])
        choices_made.append(
            {
                "node_id": str(request.node_id),
                "choice_key": request.choice_key,
                "made_at": datetime.utcnow().isoformat(),
            }
        )
        progress.choices_made = choices_made
        progress.current_node_id = next_node.id
        progress.is_completed = bool(next_node.is_end)
        progress.completion_percentage = (
            100.0 if next_node.is_end else completion_percentage
        )
        choices_made_count = len(choices_made)

    # Build next node payload
    character_response = None
    if next_node.character_id:
        char_result = await db.execute(
            select(Character).where(
                Character.id == next_node.character_id, Character.story_id == story.id
            )
        )
        character = char_result.scalar_one_or_none()
        if character:
            translated_name = character.name
            if isinstance(character.name_translations, dict):
                translated_name = character.name_translations.get(
                    language, character.name_translations.get("en", character.name)
                )
            character_response = CharacterResponse(
                id=character.id,
                slug=character.slug,
                name=translated_name,
                voice_profile=character.voice_profile,
                bulbul_speaker=character.bulbul_speaker,
                avatar_url=character.avatar_url,
            )

    next_choices = None
    if next_node.node_type == "choice":
        choice_result = await db.execute(
            select(StoryChoice).where(StoryChoice.node_id == next_node.id)
        )
        raw_choices = choice_result.scalars().all()
        if raw_choices:
            next_choices = [
                ChoiceResponse(
                    id=next_choice.id,
                    choice_key=next_choice.choice_key,
                    text=get_localized_text(next_choice.text_content, language),
                    next_node_id=next_choice.next_node_id,
                )
                for next_choice in raw_choices
            ]

    next_node_response = StoryNodeResponse(
        id=next_node.id,
        node_type=next_node.node_type,
        display_order=next_node.display_order,
        is_start=next_node.is_start,
        is_end=next_node.is_end,
        text=get_localized_text(next_node.text_content, language),
        character=character_response,
        choices=next_choices,
    )
    
    return MakeChoiceResponse(
        success=True,
        choice_made={
            "node_id": request.node_id,
            "choice_key": request.choice_key,
            "choice_text": get_localized_text(choice.text_content, language),
        },
        next_node=next_node_response,
        progress={
            "completion_percentage": 100.0 if next_node.is_end else completion_percentage,
            "choices_made_count": choices_made_count,
        }
    )
