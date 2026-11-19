from src.services.exceptions import NoDataError, SiteUnreachableError
from src.kafka.consumer import KafkaConsumerService
from src.services.rosstat_service import RosstatService
from src.logger_core.logging_config import logger
from src.core.database import async_session
from src.repositories.inn_repository import InnRepository
from src.core.pool import pool
from src.schemas.inn_schemas import InnStatus
import asyncio


async def update_task_status(
     task_id: str,
     status: InnStatus,
     data: dict | None = None,
     error:str = ""
) -> None:
    async with async_session() as session:
        if status == InnStatus.FAILED:
            await InnRepository.fail_task(session, task_id, error)
        elif status == InnStatus.COMPLETED:
            await InnRepository.complete_task(session, task_id, data)
        await session.commit()


async def handle_inn(data: dict) -> None:
    task_id = data.get("task_id")
    inn = data.get("inn")

    if not task_id or not inn:
        logger.warning("Invalid message, skip: %s", data)
        return

    logger.info("Processing: task_id=%s inn=%s", task_id, inn)


    try:
        async with pool.page() as page:
            service = RosstatService(page)
            result = await service.get_results_by_inn(inn)

        if not result:
            logger.error("No data found for inn: %s", inn)
            raise NoDataError(f"No data found for inn {inn}")

    except (SiteUnreachableError, NoDataError) as e:
        logger.warning("Expected error: task_id=%s inn=%s error=%s", task_id, inn, e)
        await update_task_status(task_id, InnStatus.FAILED, error=str(e))
        return

    except Exception as e:
        logger.exception("Unexpected error: task_id=%s inn=%s", task_id, inn)
        await update_task_status(task_id, InnStatus.FAILED, error=str(e))
        raise

    await update_task_status(task_id, InnStatus.COMPLETED, data={"results": result})
    logger.info("Completed: task_id=%s inn=%s", task_id, inn)




async def main() -> None:
    await pool.start()
    logger.info("Browser pool started")

    consumer = KafkaConsumerService()
    await consumer.start()

    try:
        await consumer.fetch_messages(handle_inn)
    finally:
        await consumer.stop()
        await pool.stop()
        logger.info("Browser pool stopped")

if __name__ == "__main__":
    asyncio.run(main())