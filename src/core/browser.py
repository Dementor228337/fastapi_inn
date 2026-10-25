from contextlib import asynccontextmanager
from typing import AsyncIterator

from playwright.async_api import async_playwright, Page, Browser, BrowserContext, Playwright

from src.core.config import settings



class BrowserManager:
    """
    Управляет жизненным циклом Playwright и браузера.

    Отвечает за запуск браузера, создание контекста и вкладки (Page).

    Настроен на обход базовых антибот-защит (скрывает navigator.webdriver,
    подменяет User-Agent).

    Не управляет бизнес-логикой парсинга, а только предоставляет
    готовую вкладку для работы.
    """


    def __init__(self) -> None:
        """
        Инициализация менеджера.
        :return: None
        """
        self._playwright: Playwright | None = None
        self._browser: Browser | None = None
        self._browser_context: BrowserContext | None = None

    async def start(self) -> Page:
        """
        Запускает Playwright, браузер и создает новую страницу.
        :return: Объект класса Page.
        """
        self._playwright = await async_playwright().start()

        self._browser = await self._playwright.chromium.launch(
            headless=settings.headless,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-setuid-sandbox",
            ]
        )
        self._browser_context = await self._browser.new_context(
            ignore_https_errors=settings.ignore_https_errors,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) "
                       "Chrome/122.0.0.0 Safari/537.36"
            )

        await self._browser_context.add_init_script("""
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    });
                """)

        self._browser_context.set_default_timeout(settings.default_timeout_ms)

        return await self._browser_context.new_page()

    async def close(self) -> None:
        """
        Закрывает контекст, браузер и останавливает Playwright.
        Порядок закрытия: контекст -> браузер -> Playwright.
        :return: None.
        """
        if self._browser_context:
            await self._browser_context.close()
        if self._browser:
            await self._browser.close()
        if self._playwright:
            await self._playwright.stop()

@asynccontextmanager
async def browser_page() -> AsyncIterator[Page]:
    """
    Асинхронный контекстный менеджер для работы с браузером.

    Автоматически запускает браузер при входе в блок `async with`
    и гарантированно закрывает его при выходе (даже если внутри
    произошло исключение).
    :yield: Объект класса Page.
    """
    manager = BrowserManager()
    page = await manager.start()
    try:
        yield page
    finally:
        await manager.close()
