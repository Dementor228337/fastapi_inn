from pathlib import Path
from openpyxl import Workbook
from src.logger_core.logging_config import logger



def write_excel(
        rows: list[dict[str, str]],
        path: Path
    ) -> Path:
    """Пишет список словарей в Excel-файл."""

    logger.debug(f"Запись Excel: {len(rows)} строк → {path}")

    path.parent.mkdir(parents=True, exist_ok=True)

    wb = Workbook()
    ws = wb.active
    for row in rows:
        for key, value in row.items():
            ws.append([key, value])

    wb.save(path)
    logger.debug(f"Excel-файл записан: {path.name}")
    return path