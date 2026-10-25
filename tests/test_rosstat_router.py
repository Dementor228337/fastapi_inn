from pathlib import Path
from unittest.mock import patch, AsyncMock
from services.exceptions import (
NoDataError,
SiteUnreachableError,
FileSaveError
)

"""
Тесты FastAPI роутера и HTTP-ошибок, которые он отлавливает.
Все тесты используют фикстуру `client` из `tests/conftest.py` — это
экземпляр `TestClient`, который делает HTTP-запросы к приложению
без реального сервера. Каждый тест получает свежий `client`,
поэтому состояние (cookies, headers) не течёт между тестами.
"""


async def test_inn(client):
    """
    Базовая проверка работоспособность эндпоинта.
    Должен возвращать 200 статус и ответ в формате JSON,
    где будет отображен статус и имя созданного файла.
    """
    with patch(
        "src.services.rosstat_service.RosstatService.export_forms_by_inn",
        new=AsyncMock(return_value=Path("505021556592.xlsx")),
    ):
        response = client.post("/forms/505021556592")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["file_path"].endswith(".xlsx")


async def test_inn_no_data(client):
    """
    Тест энпоинта с принудительно вызванной ошибкой.
    Должен вернуть 404.
    """
    with patch(
            "src.services.rosstat_service.RosstatService.export_forms_by_inn",
            new=AsyncMock(side_effect=NoDataError("Данных нет")),
    ):
        response = client.post("/forms/505021556592")

    assert response.status_code == 404
    assert response.json()["detail"] == "Данных нет"


async def test_inn_site_down(client):
    """
    Тест энпоинта при недоступном сайте Росстата.
    Должен вернуть 503.
    """
    with patch(
            "src.services.rosstat_service.RosstatService.export_forms_by_inn",
            new=AsyncMock(side_effect=SiteUnreachableError("Timeout")),
    ):
        response = client.post("/forms/505021556592")

    assert response.status_code == 503


async def test_inn_file_busy(client):
    """
    Тест энпоинта при невозможности достучаться до файла.
    Должен вернуть 409.
    """
    with patch(
            "src.services.rosstat_service.RosstatService.export_forms_by_inn",
            new=AsyncMock(side_effect=FileSaveError("Файл занят")),
    ):
        response = client.post("/forms/505021556592")

    assert response.status_code == 409


async def test_inn_unexpected_error(client):
    """
    Тест на отлавливание любой другой непредвиденной ошибки
    Должен возвращать 500.
    :param client:
    :return:
    """
    with patch(
            "src.services.rosstat_service.RosstatService.export_forms_by_inn",
            new=AsyncMock(side_effect=RuntimeError("Что-то сломалось")),
    ):
        response = client.post("/forms/505021556592")

    assert response.status_code == 500
    assert response.json()["detail"] == "Внутренняя ошибка сервера"