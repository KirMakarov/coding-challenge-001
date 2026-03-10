from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path

import pytest
from external_resources.invoice_data import Invoice, extract_invoice_data


def test_invoice_create():
    inv = Invoice.create("INV-001", "200.01", "2026-01-01")

    assert inv.total_amount == Decimal("200.01")
    assert inv.due_date == date(2026, 1, 1)
    assert inv.invoice_number == "INV-001"


def test_invoice_create_invalid_amount():
    with pytest.raises(InvalidOperation):
        Invoice.create("INV-002", "10e", "2026-01-02")


def test_invoice_create_invalid_date():
    with pytest.raises(ValueError):
        Invoice.create("INV-003", "150.00", "2026-01-32")


def test_extract_invoice_data_success(mocker):
    mocker.patch("external_resources.invoice_data.Path.exists", return_value=True)
    csv_content = "invoice_number,total_amount,due_date\nINV-001,100.00,2026-01-01\n"
    mocker.patch("builtins.open", mocker.mock_open(read_data=csv_content))

    invoices = list(extract_invoice_data(Path("dummy.csv")))

    assert len(invoices) == 1
    assert invoices[0].invoice_number == "INV-001"


def test_extract_invoice_data_file_not_found(mocker):
    mocker.patch("external_resources.invoice_data.Path.exists", return_value=False)

    with pytest.raises(FileNotFoundError):
        list(extract_invoice_data(Path("missing.csv")))


def test_extract_invoice_data_invalid_columns(mocker):
    mocker.patch("external_resources.invoice_data.Path.exists", return_value=True)
    csv_content = "id,amount,date\n1,100.00,2026-01-01\n"
    mocker.patch("builtins.open", mocker.mock_open(read_data=csv_content))

    with pytest.raises(ValueError):
        list(extract_invoice_data(Path("invalid_columns.csv")))


@pytest.mark.parametrize(
    "csv_content",
    [
        "invoice_number,total_amount,due_date\nINV-001,100.00\n\nINV-002,200.00,2026-01-02\n",
        "invoice_number,total_amount,due_date\nINV-001,,2026-01-02\n\nINV-002,200.00,2026-01-02\n",
        "invoice_number,total_amount,due_date\nINV-001,100.00,2026-01-32\n\nINV-002,200.00,2026-01-02\n",
        "invoice_number,total_amount,due_date\nINV-001,100.0e,2026-01-32\n\nINV-002,200.00,2026-01-02\n",
    ],
)
def test_extract_invoice_data_should_skip_invalid_row(mocker, csv_content):
    mocker.patch("external_resources.invoice_data.Path.exists", return_value=True)
    mocker.patch("builtins.open", mocker.mock_open(read_data=csv_content))
    mocker.patch("builtins.open", mocker.mock_open(read_data=csv_content))

    invoices = list(extract_invoice_data(Path("invalid_row.csv")))

    assert len(invoices) == 1
    assert invoices[0].invoice_number == "INV-002"


# def test_extract_invoice_data_invalid_amount(mocker):
#     mocker.patch("external_resources.invoice_data.Path.exists", return_value=True)
#     csv_content = (
#         "invoice_number,total_amount,due_date\nINV-001,invalid_amount,2026-01-01\n"
#     )
#     mocker.patch("builtins.open", mocker.mock_open(read_data=csv_content))

#     with pytest.raises(ValueError):
#         list(extract_invoice_data(Path("invalid_amount.csv")))


# def test_extract_invoice_data_invalid_date(mocker):
#     mocker.patch("external_resources.invoice_data.Path.exists", return_value=True)
#     csv_content = "invoice_number,total_amount,due_date\nINV-001,100.00,invalid_date\n"
#     mocker.patch("builtins.open", mocker.mock_open(read_data=csv_content))

#     with pytest.raises(ValueError):
#         list(extract_invoice_data(Path("invalid_date.csv")))
