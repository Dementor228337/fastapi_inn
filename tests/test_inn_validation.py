"""
Тесты для валидации ИНН.
Все тесты используют фикстуру `client` из `tests/conftest.py` — это
экземпляр `TestClient`, который делает HTTP-запросы к приложению
без реального сервера. Каждый тест получает свежий `client`,
поэтому состояние (cookies, headers) не течёт между тестами.
"""


async def test_invalid_inn(client):
        """
        Возващает 422, если формат ИНН некорректен (буквы вместо цифр).
        """
        response = client.post("/forms/inn")
        assert response.status_code == 422


async def test_inn_too_short(client):
        """
        Возващает 422, если формат ИНН некорректен (слишком короткий).
        """
        response = client.post("/forms/12345")
        assert response.status_code == 422


async def test_inn_too_long(client):
        """
        Возващает 422, если формат ИНН некорректен (слишком длинный).
        """
        response = client.post("/forms/1234567890123")
        assert response.status_code == 422
