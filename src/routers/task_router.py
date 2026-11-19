from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.database import get_db
from src.repositories.inn_repository import InnRepository
from src.schemas.inn_schemas import InnResultResponse
task_router = APIRouter(prefix="/results")

@task_router.get("/{task_id}", response_model=InnResultResponse)
async def get_task(
    task_id: str,
    session: AsyncSession = Depends(get_db),
):
    row = await InnRepository.get_task(session, task_id)

    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    return row