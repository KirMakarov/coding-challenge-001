import csv
from datetime import date
from decimal import Decimal
from pathlib import Path

from external_resources.bank import Transaction
from external_resources.invoice_data import Invoice
from external_resources.reconciliation_report import ReconciliationReport


def test_export_to_csv_standard_data(tmp_path):
    matched_invoice = Invoice("INV-001", Decimal("100.00"), date(2026, 1, 1))
    matched_transaction = Transaction(
        "INV-001", Decimal("100.00"), date(2026, 1, 1), "Payment for INV-001"
    )

    unmatched_invoice = Invoice("INV-002", Decimal("200.00"), date(2026, 1, 2))
    unmatched_transaction = Transaction(
        "IN-002", Decimal("300.00"), date(2026, 1, 3), "Unknown payment"
    )

    report = ReconciliationReport(
        reconciled=[(matched_invoice, matched_transaction)],
        unmatched_invoices=[unmatched_invoice],
        unmatched_transactions=[unmatched_transaction],
    )

    csv_file = tmp_path / "standard_summary.csv"
    report.export_to_csv(csv_file)

    assert csv_file.exists()

    with open(csv_file, mode="r", encoding="utf-8") as f:
        reader = list(csv.reader(f))

        assert len(reader) == 3, "Expected 3 rows in the CSV (header + 2 data rows)"
        assert reader[0] == ["type", "date", "amount", "invoice_number", "transaction_id", "transaction_note"]
        assert reader[1] == ["unmatched_invoice","2026-01-02","200.00","INV-002","",""]
        assert reader[2] == ["unmatched_transaction","2026-01-03","300.00","","IN-002","Unknown payment"]


def test_export_to_csv_empty_report(tmp_path):
    report = ReconciliationReport(
        reconciled=[], unmatched_invoices=[], unmatched_transactions=[]
    )

    csv_file = tmp_path / "empty_summary.csv"
    report.export_to_csv(csv_file)

    with open(csv_file, mode="r", encoding="utf-8") as f:
        reader = list(csv.reader(f))

        assert len(reader) == 1, "Expected only the header row in the CSV for an empty report"
        assert reader[0] == ["type", "date", "amount", "invoice_number", "transaction_id", "transaction_note"]
