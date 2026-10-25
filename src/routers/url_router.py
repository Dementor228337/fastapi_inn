from fastapi import APIRouter, HTTPException, status, Path
from src.services.exceptions import NoDataError, SiteUnreachableError, FileSaveError
from src.services.rosstat_service import RosstatService
from src.core.browser import browser_page

inn_router = APIRouter(
    prefix="/forms",
    tags=["Формы"],
)

@inn_router.post(
    "/{inn}",
    summary="Сохранить данные по ИНН в Excel-файл"
)
async def form_by_inn(
        inn: str = Path(..., pattern=r"^\d{10}$|^\d{12}$")
):
    """
    Эндпоинт для сохранения данных с сайта Росстата в Excel-файл.
    :param inn: ИНН в виде строки.
    :return: Ответ в формате JSON со статусом выполнения и названием файла.
    """
    try:
        async with browser_page() as page:
            service = RosstatService(page)
            file_path = await service.export_forms_by_inn(inn)

        return {
            "status": "success",
            "file_path": file_path.name
        }

    except NoDataError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

    except SiteUnreachableError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e)
        )

    except FileSaveError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        )