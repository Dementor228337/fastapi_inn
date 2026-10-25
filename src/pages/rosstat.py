from playwright.async_api import Page, Locator
from src.core.config import settings


class RosstatMainPage:
    URL = settings.base_url

    """
    Главная страница сайта Росстата.
    Предоставляет доступ к функциям для навигации по ее разделам.
    """

    def __init__(self, page: Page) -> None:
        """
        Инициализация страницы сайта.
        :param page: Экземпляр класса Page.
        :return: None
        """
        self.page = page

    @property
    def respondents_link(self) -> Locator:
        """
        Обнаружение ссылки "Респондентам.
        :return: Объект класса Locator.
        """
        return self.page.get_by_text("Респондентам").first

    @property
    def inn_link(self) -> Locator:
        """
        Обнаружение ссылки для перехода на страницу, где будет вводиться ИНН.
        :return: Объект класса Locator.
        """
        return self.page.get_by_text(
            "Индивидуальный перечень форм по ИНН / ОГРН (ОГРНИП) / ОКПО"
        )

    async def open(self) -> None:
        """
        Переход на сайт Росстата по url.
        :return: None.
        """

        await self.page.route(
            "**/browser-updater/**",
            lambda route: route.abort()
        )

        await self.page.goto(
            self.URL,
            wait_until="domcontentloaded"
        )

        try:
            cookie_btn = self.page.get_by_role("button", name="Я согласен")
            if await cookie_btn.is_visible(timeout=1000):
                await cookie_btn.click()

        except Exception as e:
            print(f"Parsing error: {e}")
            raise

        await self.respondents_link.wait_for(state="visible", timeout=20000)


    async def go_to_respondents(self) -> None:
        """
        Функция для перехода по на страницу ввода ИНН через вкладку 'Респондентам'.
        :return: None.
        """
        await self.respondents_link.hover()
        item = self.inn_link
        await item.wait_for(state="visible")
        await item.click()


class RosstatInnPage:
    """
    Класс для поиска форм по ИНН и таблица результатов
    """

    def __init__(self, page: Page) -> None:
        """
        Инициализация страницы сайта для работы с ИНН и результирующей таблицей.
        :param page: Экземпляр класса Page.
        :return: None
        """
        self.page = page

    @property
    def inn_field(self) -> Locator:
        """
        Функция для обнаружения поля 'ИНН' для последующего заполнения.
        :return: Объект класса Locator.
        """

        return self.page.locator("#inn")

    @property
    def submit_button(self) -> Locator:
        """
        Функция для обнаружения кнопки 'Получить' для последующего её нажатия.
        :return: Объект класса Locator.
        """

        return self.page.get_by_role("button", name="Получить")

    @property
    def result_table(self) -> Locator:
        """
        Функция для обнаружения таблицы данных.
        Таблица появится после заполнения поля 'ИНН' и нажатия кнопки 'Получить'.
        :return: Объект класса Locator.
        """

        return self.page.locator("table").first

    @property
    def result_rows(self) -> Locator:
        """Локатор для всех строк таблицы с результатами.
        Находит элементы <tr> внутри <tbody> первой таблицы на странице.
        Если на странице есть вложенные таблицы, локатор захватит и их строки тоже.
        :return: Объект класа Locator.
        """

        return self.result_table.locator("tbody tr")

    async def fill_inn(self, inn: str) -> None:
        """
        Асинхронная функция для заполнения поля ИНН после того, как оно прогрузится.
        :param inn: ИНН в виде строки.
        :return: None.
        """
        await self.inn_field.wait_for(state="visible")
        await self.inn_field.fill(inn)

    async def submit(self) -> None:
        """
        Асинхронная функция для нажатия кнопки 'Получить'.
        :return: None.
        """

        await self.submit_button.click()

    async def wait_for_result(self, timeout: int = 10000) -> None:
        """
        Асинхронная функция для ожидания появления результирующей таблицы на сайте.
        Время ожидания по умолчанию составляет 10 секунд.
        :param timeout: Число, отражающее миллисекунды.
        :return: None
        """
        await self.result_table.wait_for(state="visible", timeout=timeout)

    async def get_table(self) -> list[dict[str, str]]:
        """
        Асинхронная функция для получения результирующей таблицы по ИНН с сайта Росстата.
        :return: Список словарей, где в каждом словаре и ключ, и значение являются строками.
        """

        rows = self.result_rows
        count = await rows.count()
        result = []
        for i in range(count):
            row = rows.nth(i)
            ths = row.locator("th")
            cells = row.locator("td")

            if await ths.count():
                row_name = (await ths.first.inner_text()).strip()
            else:
                row_name = f"row_{i}"

            cells_count = await cells.count()
            values = []
            for j in range(cells_count):
                text = await cells.nth(j).inner_text()
                values.append(text.strip())

            result.append({row_name: '; '.join(values)})
        return result



async def parse_table_html(html: str) -> list[dict[str, str]]:
    """
    Функция для парсинга таблицы без использования Playwright.
    Написана для облегчения тестирования.
    :param html: Принимает HTML в виде строки.
    :return: Список словарей, где и ключ, и значения представляют собой строки.
    """
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, "html.parser")
    result = []
    for row in soup.select("table tbody tr"):
        th = row.select_one("th")
        tds = row.select("td")
        if not th or not tds:
            continue
        name = th.text.strip()
        values = [td.text.strip() for td in tds]
        result.append({name: "; ".join(values)})
    return result
