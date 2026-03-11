import csv
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Generator

from utils.logger import get_logger

logger = get_logger(__name__)

INVOICE_DATA_CSV_PATH = Path(__file__).parent / "invoice_data.csv"
INVOICE_AMOUNT_OF_COLUMNS = 3
INVOICE_DATA_COLUMNS = {"invoice_number", "total_amount", "due_date"}


@dataclass
class Invoice:
    invoice_number: str
    total_amount: Decimal
    due_date: date

    @classmethod
    def create(
        cls,
        invoice_number: str,
        total_amount: str | Decimal,
        due_date: str | date,
    ):
        if not isinstance(total_amount, Decimal):
            total_amount = Decimal(total_amount)
        if isinstance(due_date, str):
            due_date = datetime.strptime(due_date, "%Y-%m-%d").date()
        return cls(invoice_number, total_amount=total_amount, due_date=due_date)

    def __repr__(self):
        return f"Invoice: number - {self.invoice_number}, amount - {self.total_amount}, due_date - {self.due_date}"


def is_valid_invoice_row(row: dict[str, str | None]) -> bool:
    return all(cell and cell.strip() for cell in row.values())


def extract_invoice_data(
    source: Path | None = None,
) -> Generator[Invoice, None, None]:
    """Extracts invoice data from a CSV file and yields Invoice instances."""
    if source is None:
        source = INVOICE_DATA_CSV_PATH

    if not source.exists():
        raise FileNotFoundError(f"Invoice data file not found at: {source}")

    with open(source, "r") as invoice_file:
        csv_reader = csv.DictReader(invoice_file)

        if not INVOICE_DATA_COLUMNS.issubset(set(csv_reader.fieldnames or [])):
            raise ValueError(
                f"Invalid invoice data columns. Expected: {INVOICE_DATA_COLUMNS}, got: {csv_reader.fieldnames}"
            )

        for row in csv_reader:
            if not is_valid_invoice_row(row):
                continue
            logger.debug(f"Processing row: {row}")
            try:
                yield Invoice.create(**row)
            except (ValueError, InvalidOperation) as e:
                logger.error(f"Error creating Invoice from row: {row}. Error: {e}")
