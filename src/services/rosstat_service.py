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

from src.logger_core.logging_config import logger

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

        logger.info(f"Начало получения данных по ИНН: {inn}")

        try:
            main_page = RosstatMainPage(self.page)
            await main_page.open()
            await main_page.go_to_respondents()

            inn_page = RosstatInnPage(self.page)
            await inn_page.fill_inn(inn)
            await inn_page.submit()

            logger.debug(f"Ожидание загрузки результатов для ИНН: {inn}")
            await inn_page.wait_for_result()

            result = await inn_page.get_table()

            logger.info(f"Успешно получены данные по ИНН {inn}. Найдено строк: {len(result)}")
            return result

        except PlaywrightTimeoutError as e:
            logger.error(f"Таймаут при работе с сайтом Росстата для ИНН {inn}: {e}", exc_info=True)
            raise SiteUnreachableError(
                f"Сайт Росстата не ответил вовремя при обработке ИНН {inn}"
            ) from e

        except PlaywrightError as e:
            logger.error(f"Сбой браузера (Playwright) при обработке ИНН {inn}: {e}", exc_info=True)
            raise SiteUnreachableError(f"Сбой браузера при обработке ИНН {inn}") from e


    async def export_forms_by_inn(self, inn: str) -> Path:
        """
        Асинхронная функция для экспортирования полученных с сайта данных в Excel-файл.
        :param inn: Инн в виде строки.
        :return: Path - путь до файла.
        """

        logger.info(f"Запрос на экспорт данных в Excel для ИНН: {inn}")

        rows = await self.get_results_by_inn(inn)
        if not rows:
            logger.warning(f"По ИНН {inn} данные не найдены (таблица пуста). Экспорт отменен.")
            raise NoDataError(f"По ИНН {inn} данные не найдены (таблица пуста)")

        file_path = settings.files_dir / f"{inn}.xlsx"

        try:
            logger.debug(f"Попытка записи файла: {file_path}")
            write_excel(rows, file_path)
            logger.info(f"Файл успешно сохранен: {file_path}")
            return file_path

        except PermissionError as e:
            logger.error(
                f"Ошибка доступа при сохранении файла {file_path.name}: "
                f"файл занят другой программой",
                exc_info=True
            )
            raise FileSaveError(
                f"Файл {file_path.name} открыт в другой программе или доступен только для чтения"
            ) from e

        except OSError as e:
            logger.error(
                f"Системная ошибка при сохранении файла {file_path.name}: {e}",
                exc_info=True
            )
            raise FileSaveError(f"Не удалось сохранить файл {file_path.name}") from e