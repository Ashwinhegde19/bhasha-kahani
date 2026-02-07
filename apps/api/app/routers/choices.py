from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from typing import Optional

from app.database import get_db
from app.models.story import Story, StoryNode, StoryChoice
from app.models.progress import UserProgress
from app.schemas.story import MakeChoiceRequest, MakeChoiceResponse, StoryNodeResponse, ChoiceResponse

router = APIRouter()


@router.post("/{slug}/choices", response_model=MakeChoiceResponse)
async def make_choice(
    slug: str,
    request: MakeChoiceRequest,
    user_id: Optional[UUID] = None,  # Get from JWT in production
    db: AsyncSession = Depends(get_db)
):
    """Make a choice and get next node"""
    # Get story
    result = await db.execute(
        select(Story).where(Story.slug == slug)
    )
    story = result.scalar_one_or_none()
    
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    
    # Get current node
    result = await db.execute(
        select(StoryNode).where(StoryNode.id == request.node_id)
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
            select(StoryNode).where(StoryNode.id == choice.next_node_id)
        )
        next_node = result.scalar_one_or_none()
    
    if not next_node:
        raise HTTPException(status_code=404, detail="Next node not found")
    
    # Update user progress if user_id provided
    if user_id:
        result = await db.execute(
            select(UserProgress).where(
                UserProgress.user_id == user_id,
                UserProgress.story_id == story.id
            )
        )
        progress = result.scalar_one_or_none()
        
        if progress:
            progress.current_node_id = next_node.id
            choices_made = progress.choices_made or []
            choices_made.append({
                "node_id": str(request.node_id),
                "choice": request.choice_key
            })
            progress.choices_made = choices_made
    
    # Build response
    next_node_response = StoryNodeResponse(
        id=next_node.id,
        node_type=next_node.node_type,
        display_order=next_node.display_order,
        is_start=next_node.is_start,
        is_end=next_node.is_end,
        text=next_node.text_content.get("en", ""),  # TODO: Get language
        character=None,  # TODO: Add character
        choices=None  # Will be populated by frontend
    )
    
    return MakeChoiceResponse(
        success=True,
        choice_made={
            "node_id": request.node_id,
            "choice_key": request.choice_key,
            "choice_text": choice.text_content.get("en", "")
        },
        next_node=next_node_response,
        progress={
            "completion_percentage": 50.0,  # Calculate based on story
            "choices_made_count": 1
        }
    )
