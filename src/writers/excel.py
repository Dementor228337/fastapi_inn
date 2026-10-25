from pathlib import Path
from openpyxl import Workbook




def write_excel(
        rows: list[dict[str, str]],
        path: Path
    ) -> Path:
    """Пишет список словарей в Excel-файл."""
    path.parent.mkdir(parents=True, exist_ok=True)

    wb = Workbook()
    ws = wb.active
    for row in rows:
        for key, value in row.items():
            ws.append([key, value])

    wb.save(path)
    return path