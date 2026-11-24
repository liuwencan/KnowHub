import csv
import io
from pathlib import Path
from typing import Any


def parse_text(content: bytes, encoding: str = "utf-8") -> str:
    return content.decode(encoding, errors="replace")


def parse_csv_rows(content: bytes, encoding: str = "utf-8") -> list[list[str]]:
    return [row for row in csv.reader(io.StringIO(parse_text(content, encoding)))]


def parse_excel_rows(content: bytes) -> list[list[Any]]:
    try:
        import openpyxl
    except ImportError as error:
        raise RuntimeError("Excel parsing requires the optional openpyxl dependency") from error
    workbook = openpyxl.load_workbook(io.BytesIO(content), read_only=True, data_only=True)
    worksheet = workbook.active
    return [list(row) for row in worksheet.iter_rows(values_only=True)]


def parse_file(path: str | Path) -> str | list[list[Any]]:
    source = Path(path)
    content = source.read_bytes()
    if source.suffix.lower() == ".csv":
        return parse_csv_rows(content)
    if source.suffix.lower() in {".xlsx", ".xlsm"}:
        return parse_excel_rows(content)
    return parse_text(content)
