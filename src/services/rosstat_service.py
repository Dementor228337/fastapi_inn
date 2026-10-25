from pathlib import Path
from src.services.exceptions import SiteUnreachableError, NoDataError, FileSaveError
from src.core.config import settings
from src.pages.rosstat import RosstatInnPage, RosstatMainPage

from playwright.async_api import (
Page,
TimeoutError as PlaywrightTimeoutError,
Error as PlaywrightError
)

from src.writers.excel import write_excel



class RosstatService:
    """Сервис для работы с сайтом Росстата."""

    def __init__(self, page: Page) -> None:
        self.page = page


    async def get_results_by_inn(
            self, inn: str
    ) -> list[dict[str, str]]:
        """
        Асинхронная функция для получения информации по ИНН в виде списка словарей.
        :param inn: Инн в виде строки.
        :return: список словарей, где в каждом словаре и ключ, и значение являются строками.
        """

        try:
            main_page = RosstatMainPage(self.page)
            await main_page.open()
            await main_page.go_to_respondents()

            inn_page = RosstatInnPage(self.page)
            await inn_page.fill_inn(inn)
            await inn_page.submit()
            await inn_page.wait_for_result()
            return await inn_page.get_table()

        except PlaywrightTimeoutError as e:
            raise SiteUnreachableError(
                f"Сайт Росстата не ответил вовремя при обработке ИНН {inn}"
            ) from e

        except PlaywrightError as e:
            raise SiteUnreachableError(f"Сбой браузера при обработке ИНН {inn}") from e


    async def export_forms_by_inn(self, inn: str) -> Path:
        """
        Асинхронная функция для экспортирования полученных с сайта данных в Excel-файл.
        :param inn: Инн в виде строки.
        :return: Path - путь до файла.
        """

        rows = await self.get_results_by_inn(inn)
        if not rows:
            raise NoDataError(f"По ИНН {inn} данные не найдены (таблица пуста)")

        file_path = settings.files_dir / f"{inn}.xlsx"

        try:
            write_excel(rows, file_path)
            return file_path

        except PermissionError as e:
            raise FileSaveError(
                f"Файл {file_path.name} открыт в другой программе или доступен только для чтения"
            ) from e

        except OSError as e:
            raise FileSaveError(f"Не удалось сохранить файл {file_path.name}") from e