from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from uuid import UUID

from app.database import get_db
from app.models.story import Story, StoryTranslation, Character, StoryNode, StoryChoice
from app.schemas.story import (
    StoryListResponse, StoryDetailResponse, StoryResponse, 
    StoryNodeResponse, CharacterResponse, ChoiceResponse
)

router = APIRouter()


@router.get("", response_model=StoryListResponse)
async def list_stories(
    language: Optional[str] = Query("en", description="Language code"),
    age_range: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """List all stories with pagination"""
    # Get stories with translations
    query = select(Story, StoryTranslation).join(
        StoryTranslation, Story.id == StoryTranslation.story_id
    ).where(
        StoryTranslation.language_code == language,
        Story.is_active == True
    )
    
    if age_range:
        query = query.where(Story.age_range == age_range)
    
    result = await db.execute(query)
    rows = result.all()
    
    stories = []
    for story, translation in rows:
        stories.append(StoryResponse(
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
            character_count=0,  # TODO: Fix async relationship loading
            choice_count=0,  # Calculate if needed
            is_completed_translation=translation.is_complete,
            created_at=story.created_at
        ))
    
    return StoryListResponse(
        data=stories,
        pagination={
            "page": 1,
            "limit": len(stories),
            "total": len(stories),
            "total_pages": 1,
            "has_next": False,
            "has_prev": False
        }
    )


@router.get("/{slug}", response_model=StoryDetailResponse)
async def get_story(
    slug: str,
    language: Optional[str] = Query("en", description="Language code"),
    db: AsyncSession = Depends(get_db)
):
    """Get story details with nodes and choices"""
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
            StoryTranslation.language_code == language
        )
    )
    translation = result.scalar_one_or_none()
    
    if not translation:
        # Fallback to English
        result = await db.execute(
            select(StoryTranslation).where(
                StoryTranslation.story_id == story.id,
                StoryTranslation.language_code == "en"
            )
        )
        translation = result.scalar_one_or_none()
    
    # Get characters
    characters = []
    for char in story.characters:
        characters.append(CharacterResponse(
            id=char.id,
            slug=char.slug,
            name=char.name,
            voice_profile=char.voice_profile,
            bulbul_speaker=char.bulbul_speaker,
            avatar_url=char.avatar_url
        ))
    
    # Get nodes with choices
    nodes = []
    start_node_id = None
    
    for node in sorted(story.nodes, key=lambda x: x.display_order):
        if node.is_start:
            start_node_id = node.id
        
        # Get text for current language
        text_content = node.text_content.get(language, 
            node.text_content.get("en", ""))
        
        # Get character
        character = None
        if node.character:
            character = CharacterResponse(
                id=node.character.id,
                slug=node.character.slug,
                name=node.character.name,
                voice_profile=node.character.voice_profile,
                bulbul_speaker=node.character.bulbul_speaker,
                avatar_url=node.character.avatar_url
            )
        
        # Get choices
        choices = None
        if node.node_type == "choice" and node.choices:
            choices = []
            for choice in node.choices:
                choice_text = choice.text_content.get(language,
                    choice.text_content.get("en", ""))
                choices.append(ChoiceResponse(
                    id=choice.id,
                    choice_key=choice.choice_key,
                    text=choice_text,
                    next_node_id=choice.next_node_id
                ))
        
        nodes.append(StoryNodeResponse(
            id=node.id,
            node_type=node.node_type,
            display_order=node.display_order,
            is_start=node.is_start,
            is_end=node.is_end,
            text=text_content,
            character=character,
            choices=choices
        ))
    
    return StoryDetailResponse(
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
        updated_at=story.updated_at
    )
