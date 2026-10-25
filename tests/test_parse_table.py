from src.pages.rosstat import parse_table_html


async def test_parse_table():
    """
    Базовая таблица.
    """
    html = """
        <table><tbody>
          <tr><th>ИНН</th><td>505021556592</td></tr>
          <tr><th>Организация</th><td>ООО Тест</td></tr>
        </tbody></table>
        """

    result = await parse_table_html(html)

    assert result == [
        {"ИНН": "505021556592"},
        {"Организация": "ООО Тест"},
    ]


async def test_parse_multiple_td():
    """
    Несколько td должны склеиваться через ';'.
    """
    html = "<table><tbody><tr><th>Форма</th><td>1-П</td><td>Москва</td></tr></tbody></table>"
    result = await parse_table_html(html)
    assert result == [{"Форма": "1-П; Москва"}]


async def test_parse_empty_table():
    """
    Пустая таблица.
    """
    html = "<table><tbody></tbody></table>"
    result = await parse_table_html(html)
    assert result == []

async def test_parse_row_without_th():
    """
    Строка без th.
    Должна пропускаться.
    """
    html = "<table><tbody><tr><td>значение</td></tr></tbody></table>"
    result = await parse_table_html(html)
    assert result == []

