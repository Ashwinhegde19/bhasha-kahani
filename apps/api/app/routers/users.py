from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from typing import List

from app.database import get_db
from app.models.user import User
from app.models.progress import UserProgress, Bookmark
from app.models.story import Story
from app.schemas.user import UserResponse
from app.schemas.progress import ProgressResponse, ProgressSummary

router = APIRouter()


@router.get("/progress", response_model=ProgressSummary)
async def get_user_progress(
    user_id: UUID,  # In production, get from JWT token
    db: AsyncSession = Depends(get_db)
):
    """Get user's story progress"""
    result = await db.execute(
        select(UserProgress, Story).join(
            Story, UserProgress.story_id == Story.id
        ).where(UserProgress.user_id == user_id)
    )
    rows = result.all()
    
    progress_list = []
    for progress, story in rows:
        progress_list.append(ProgressResponse(
            story_id=progress.story_id,
            story_slug=story.slug,
            story_title=story.slug,  # TODO: Get from translation
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
    user_id: UUID,
    story_id: UUID,
    current_node_id: UUID,
    is_completed: bool = False,
    time_spent_sec: int = 0,
    db: AsyncSession = Depends(get_db)
):
    """Update user progress"""
    # Find or create progress
    result = await db.execute(
        select(UserProgress).where(
            UserProgress.user_id == user_id,
            UserProgress.story_id == story_id
        )
    )
    progress = result.scalar_one_or_none()
    
    if not progress:
        progress = UserProgress(
            user_id=user_id,
            story_id=story_id,
            current_node_id=current_node_id,
            play_count=1
        )
        db.add(progress)
    else:
        progress.current_node_id = current_node_id
        progress.play_count += 1
        progress.total_time_sec += time_spent_sec
    
    if is_completed:
        progress.is_completed = True
        progress.completion_percentage = 100.0
    
    await db.flush()
    
    return {"success": True}
