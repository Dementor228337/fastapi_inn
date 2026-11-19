from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent
# __file__ = src/core/config.py
# .parent               = src/core
# .parent.parent        = src
# .parent.parent.parent = корень проекта


class BrowserSettings(BaseSettings):
    """Настройки браузера для работы.
    Включает в себя дефолтный url,
    отображение тестовой страницы браузера
    и игнорирование HTTP-сертификата"""
    base_url: str = "https://rosstat.gov.ru/"
    headless: bool = True
    ignore_https_errors: bool = True
    default_timeout_ms: int = 15000

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

class KafkaSettings(BaseSettings):
    """
    Настройки кафки: сервер и инн-топик.
    """
    kafka_bootstrap_servers: str = "kafka:9092"
    kafka_topic_inn: str = "inn_parsing_tasks"
    kafka_group_id: str = "inn_parsing_group"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


class Settings(BaseSettings):
    """
    Корневые настройки приложения: браузер, кафка и файлы.
    """
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@db:5432/inn_db"
    browser: BrowserSettings = Field(default_factory=BrowserSettings)
    kafka: KafkaSettings = Field(default_factory=KafkaSettings)
    files_dir: Path = BASE_DIR / "files"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
        env_nested_delimiter="__",
        case_sensitive=False
    )


#создание экземпляра настроек
settings = Settings()
settings.files_dir.mkdir(parents=True, exist_ok=True)