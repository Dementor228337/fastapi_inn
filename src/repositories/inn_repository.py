from sqlalchemy.ext.asyncio import AsyncSession
from src.logger_core.logging_config import logger
from src.models.inn_result import InnResult
from src.schemas.inn_schemas import InnStatus
from sqlalchemy import select

class InnRepository:

    @classmethod
    async def create_task(
        cls,
        session: AsyncSession,
        task_id: str,
        inn: str,
    ) -> None:
        session.add(InnResult(task_id=task_id, inn=inn, status=InnStatus.PENDING))
        await session.flush()
        logger.info("Task created: task_id=%s, inn=%s", task_id, inn)

    @classmethod
    async def complete_task(
        cls,
        session: AsyncSession,
        task_id: str,
        data: dict,
    ) -> None:
        result = await session.execute(
            select(InnResult).where(InnResult.task_id == task_id)
        )
        row = result.scalar_one_or_none()
        if row is None:
            logger.warning("Task not found for completion: task_id=%s", task_id)
            return
        row.status = InnStatus.COMPLETED
        row.data = data
        await session.flush()
        logger.info("Task completed: task_id=%s", task_id)

    @classmethod
    async def fail_task(
        cls,
        session: AsyncSession,
        task_id: str,
        error: str,
    ) -> None:
        result = await session.execute(
            select(InnResult).where(InnResult.task_id == task_id)
        )
        row = result.scalar_one_or_none()
        if row is None:
            return
        row.status = InnStatus.FAILED
        row.error = error
        await session.flush()
        logger.warning("Task failed: task_id=%s error=%s", task_id, error)

    @classmethod
    async def get_task(
        cls,
        session: AsyncSession,
        task_id: str,
    ) -> InnResult | None:
        result = await session.execute(
            select(InnResult).where(InnResult.task_id == task_id)
        )
        return result.scalar_one_or_none()

    @classmethod
    async def get_all_tasks(
        cls,
        session: AsyncSession,
    ) -> list[InnResult]:
        result = await session.execute(
                select(InnResult).order_by(InnResult.task_id)
        )
        return result.scalars().all()

