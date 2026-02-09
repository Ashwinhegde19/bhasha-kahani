from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.database import get_db
from app.models.progress import UserProgress
from app.models.story import Story, StoryNode, StoryTranslation
from app.schemas.progress import ProgressResponse, ProgressSummary
from app.utils.auth import get_optional_user_id

router = APIRouter()


@router.get("/progress", response_model=ProgressSummary)
async def get_user_progress(
    user_id: Optional[UUID] = Query(
        None, description="Backward-compatible user id query param"
    ),
    token_user_id: Optional[UUID] = Depends(get_optional_user_id),
    language: str = Query("en", description="Preferred language for story titles"),
    db: AsyncSession = Depends(get_db)
):
    """Get user's story progress"""
    resolved_user_id = token_user_id or user_id
    if resolved_user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )

    result = await db.execute(
        select(UserProgress, Story).join(
            Story, UserProgress.story_id == Story.id
        ).where(UserProgress.user_id == resolved_user_id)
    )
    rows = result.all()

    story_ids = [story.id for _, story in rows]
    title_map = {}
    if story_ids:
        translation_result = await db.execute(
            select(StoryTranslation).where(
                StoryTranslation.story_id.in_(story_ids),
                StoryTranslation.language_code.in_([language, "en"]),
            )
        )
        for translation in translation_result.scalars().all():
            existing = title_map.get(translation.story_id)
            if existing is None or translation.language_code == language:
                title_map[translation.story_id] = translation.title

    progress_list = []
    for progress, story in rows:
        progress_list.append(ProgressResponse(
            story_id=progress.story_id,
            story_slug=story.slug,
            story_title=title_map.get(story.id, story.slug),
            cover_image=story.cover_image or "",
            current_node_id=progress.current_node_id,
            is_completed=progress.is_completed,
            completion_percentage=float(progress.completion_percentage),
            play_count=progress.play_count,
            total_time_sec=progress.total_time_sec,
            last_played_at=progress.last_played_at,
            choices_made=progress.choices_made or []
        ))
    
    return ProgressSummary(
        data=progress_list,
        summary={
            "total_stories_started": len(progress_list),
            "total_stories_completed": sum(1 for p in progress_list if p.is_completed),
            "total_time_minutes": sum(p.total_time_sec for p in progress_list) // 60
        }
    )


@router.post("/progress")
async def update_progress(
    user_id: Optional[UUID] = Query(
        None, description="Backward-compatible user id query param"
    ),
    token_user_id: Optional[UUID] = Depends(get_optional_user_id),
    story_id: UUID = Query(...),
    current_node_id: UUID = Query(...),
    is_completed: bool = False,
    time_spent_sec: int = 0,
    db: AsyncSession = Depends(get_db)
):
    """Update user progress"""
    resolved_user_id = token_user_id or user_id
    if resolved_user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )

    story_result = await db.execute(select(Story).where(Story.id == story_id))
    story = story_result.scalar_one_or_none()
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")

    node_result = await db.execute(
        select(StoryNode).where(
            StoryNode.id == current_node_id, StoryNode.story_id == story_id
        )
    )
    current_node = node_result.scalar_one_or_none()
    if not current_node:
        raise HTTPException(status_code=400, detail="Invalid node for story")

    # Find or create progress
    result = await db.execute(
        select(UserProgress).where(
            UserProgress.user_id == resolved_user_id,
            UserProgress.story_id == story_id
        )
    )
    progress = result.scalar_one_or_none()
    
    if not progress:
        progress = UserProgress(
            user_id=resolved_user_id,
            story_id=story_id,
            current_node_id=current_node_id,
            play_count=1,
            total_time_sec=max(0, time_spent_sec),
            last_played_at=datetime.utcnow(),
        )
        db.add(progress)
    else:
        progress.current_node_id = current_node_id
        progress.play_count += 1
        progress.total_time_sec += max(0, time_spent_sec)
        progress.last_played_at = datetime.utcnow()

    max_order_result = await db.execute(
        select(func.max(StoryNode.display_order)).where(StoryNode.story_id == story_id)
    )
    max_order = max_order_result.scalar() or 1
    completion_percentage = min(
        100.0, max(0.0, (current_node.display_order / max_order) * 100.0)
    )
    progress.completion_percentage = completion_percentage

    if is_completed:
        progress.is_completed = True
        progress.completion_percentage = 100.0
    
    await db.flush()
    
    return {"success": True}
