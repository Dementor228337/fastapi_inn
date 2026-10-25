from dataclasses import dataclass
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
# __file__ = src/core/config.py
# .parent               = src/core
# .parent.parent        = src
# .parent.parent.parent = корень проекта


@dataclass
class Settings:
    """Настройки браузера для работы.
    Включает в себя дефолтный url,
    отобрыжение тестовой страницы браузера
    и игнорирование HTTP-сертификата"""
    base_url: str = "https://rosstat.gov.ru/"
    headless: bool = True
    ignore_https_errors: bool = True
    files_dir: Path = BASE_DIR / "files"
    default_timeout_ms: int = 15000


#создание экземпляра настроек
settings = Settings()
settings.files_dir.mkdir(parents=True, exist_ok=True)