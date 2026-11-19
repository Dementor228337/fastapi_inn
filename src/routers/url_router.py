from fastapi import APIRouter, HTTPException, status, Path, Depends, Request

from src.schemas.inn_schemas import InnResultCreate
from src.services.exceptions import NoDataError, SiteUnreachableError, FileSaveError
from src.services.rosstat_service import RosstatService
from src.core.pool import pool
from src.logger_core.logging_config import logger
from src.core.database import get_db
from src.kafka.producer import KafkaProducerService
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from src.repositories.inn_repository import InnRepository

inn_router = APIRouter(
    prefix="/forms",
    tags=["Формы"],
)

@inn_router.post(
    "/excel/{inn}",
    summary="Сохранить данные по ИНН в Excel-файл"
)
async def form_by_inn(
        inn: str = Path(..., pattern=r"^\d{10}$|^\d{12}$"),
):
    """
    Эндпоинт для сохранения данных с сайта Росстата в Excel-файл.
    :param inn: ИНН в виде строки.
    :return: Ответ в формате JSON со статусом выполнения и названием файла.
    """
    try:
        logger.info("API Request: POST /forms/excel/%s — запрос на экспорт данных по ИНН", inn)
        async with pool.page() as page:
            service = RosstatService(page)
            file_path = await service.export_forms_by_inn(inn)

        return {
            "status": "success",
            "file_path": file_path.name
        }

    except NoDataError as e:
        logger.warning("Нет данных по ИНН %s: %s", inn, e)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

    except SiteUnreachableError as e:
        logger.error(
            "Сайт Росстата недоступен при обработке ИНН %s: %s", inn, e,
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e)
        )

    except FileSaveError as e:
        logger.error(
            "Ошибка сохранения файла по ИНН %s: %s", inn, e,
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )

    except Exception as e:
        logger.exception("Неожиданная ошибка при обработке ИНН %s: %s", inn, e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        )


@inn_router.post("/task", status_code=202)
async def check_inn(
    body: InnResultCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    task_id = str(uuid4())
    await InnRepository.create_task(db, task_id, body.inn)

    producer: KafkaProducerService = request.app.state.kafka_producer
    await producer.send_inn_task(task_id, body.inn)

    return {"status": "queued", "task_id": task_id}