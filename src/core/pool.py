from contextlib import asynccontextmanager
from typing import AsyncIterator

from playwright.async_api import Playwright, Browser, BrowserContext, async_playwright, Page
import asyncio

from core.config import settings


class BrowserPool:
    """
    Отдает один браузер для работы приложения.
    Включает в себя семафор для ограничения кол-ва вкладок.
    """

    def __init__(self, max_concurrent: int = 3) -> None:
        self._playwright: Playwright | None = None
        self._browser: Browser | None = None
        self._semaphore = asyncio.Semaphore(max_concurrent)

    async def start(self) -> None:
        self._playwright = await async_playwright().start()
        self._browser = await self._playwright.chromium.launch(
            headless=settings.headless,
        )

    async def stop(self) -> None:
        if self._browser:
            await self._browser.close()
        if self._playwright:
            await self._playwright.stop()

    @asynccontextmanager
    async def page(self) -> AsyncIterator[Page]:
        """
        Выдает новую вкладку, но не более max_concurrent одновременно.
        """

        if self._browser is None:
            raise RuntimeError("BrowserPool не запущен. Необходимо вызвать pool.start()")

        async with self._semaphore:
            context = await self._browser.new_context(
                ignore_https_errors=settings.ignore_https_errors,
            )
            context.set_default_timeout(settings.default_timeout_ms)

            try:
                page = await context.new_page()
                yield page
            finally:
                await context.close()

pool = BrowserPool()