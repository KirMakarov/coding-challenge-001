from datetime import date
from decimal import Decimal

import pytest
from external_resources.bank import BankAPIClient, Transaction
from external_resources.invoice_data import Invoice
from reconciliation import Reconciliation


@pytest.mark.parametrize(
    "transaction, invoice",
    [
        (
            Transaction(
                id="1",
                amount=Decimal("100.00"),
                date=date(2026, 1, 1),
                note="Payment for INV-001",
            ),
            Invoice(
                invoice_number="INV-001",
                total_amount=Decimal("100.00"),
                due_date=date(2026, 1, 1),
            ),
        ),
        (
            Transaction(
                id="2",
                amount=Decimal("100.00"),
                date=date(2026, 1, 1),
                note="INV-002 payment",
            ),
            Invoice(
                invoice_number="INV-002",
                total_amount=Decimal("100.00"),
                due_date=date(2026, 1, 1),
            ),
        ),
    ],
)
def test_generate_report_matching_logic(mocker, transaction, invoice):
    mocker.patch.object(
        BankAPIClient,
        "fetch_transactions",
        return_value=iter([transaction]),
    )
    mocker.patch(
        "reconciliation.engine.extract_invoice_data", return_value=iter([invoice])
    )
    reconciliation = Reconciliation()

    report = reconciliation.generate_report()

    assert len(report.reconciled) == 1
    assert len(report.unmatched_invoices) == 0
    assert len(report.unmatched_transactions) == 0


@pytest.mark.parametrize(
    "transaction, invoice",
    [
        (
            Transaction(
                id="2",
                amount=Decimal("100.00"),
                date=date(2026, 1, 1),
                note="Payment for INV-001",
            ),
            Invoice(
                invoice_number="INV-002",
                total_amount=Decimal("100.00"),
                due_date=date(2026, 1, 1),
            ),
        ),  # dismatching invoice number in note
        (
            Transaction(
                id="3",
                amount=Decimal("100.00"),
                date=date(2026, 1, 1),
                note="No reference",
            ),
            Invoice(
                invoice_number="INV-003",
                total_amount=Decimal("100.00"),
                due_date=date(2026, 1, 1),
            ),
        ),  # No invoice reference in note
        (
            Transaction(
                id="4",
                amount=Decimal("100.00"),
                date=date(2026, 1, 1),
                note="Payment for INV-004",
            ),
            Invoice(
                invoice_number="INV-004",
                total_amount=Decimal("200.00"),
                due_date=date(2026, 1, 1),
            ),
        ),  # Amount mismatch
        (
            Transaction(
                id="5",
                amount=Decimal("100.00"),
                date=date(2026, 1, 1),
                note="Payment for INV-005",
            ),
            Invoice(
                invoice_number="INV-005",
                total_amount=Decimal("100.00"),
                due_date=date(2026, 1, 2),
            ),
        ),  # Date mismatch
    ],
)
def test_generate_report_matching_logic_no_match(mocker, transaction, invoice):
    mocker.patch.object(
        BankAPIClient,
        "fetch_transactions",
        return_value=iter([transaction]),
    )
    mocker.patch(
        "reconciliation.engine.extract_invoice_data", return_value=iter([invoice])
    )
    reconciliation = Reconciliation()

    report = reconciliation.generate_report()

    assert len(report.reconciled) == 0
    assert len(report.unmatched_invoices) == 1
    assert len(report.unmatched_transactions) == 1
