import pytest
from external_resources import invoice_data
from external_resources.mock_bank_api import MockBankAPIServer, MockHttpResponse
from reconciliation import Reconciliation


@pytest.fixture
def mock_csv_file(mocker, tmp_path):
    csv_file = tmp_path / "test_invoices.csv"
    content = (
        "invoice_number,total_amount,due_date\n"
        "INV-642,42.01,2026-01-11\n"  # Will match
        "INV-987,13.00,2026-01-02\n"  # Will mismatch amount
        "INV-123,301.00,2026-01-04\n"  # Will be missing in bank
        "INV-999,718.00,2026-02\n"  # Invalid date, should be skipped
    )
    csv_file.write_text(content)

    mocker.patch("external_resources.invoice_data.INVOICE_DATA_CSV_PATH", csv_file)

    return csv_file


@pytest.fixture
def mock_bank_api_server(mocker):
    server = MockBankAPIServer()
    mocker.patch.object(MockBankAPIServer, "get_transactions", server.get_transactions)

    transactions = [
        {
            "id": "1",
            "amount": 42.01,
            "date": "2026-01-11",
            "note": "Payment for INV-642",
        },  # Match
        {
            "id": "2",
            "amount": 12.00,
            "date": "2026-01-02",
            "note": "Payment for INV-987",
        },  # Mismatch amount
        {
            "id": "3",
            "amount": 301.00,
            "date": "2026-01-03",
            "note": "Payment for INV-123",
        },  # Missing invoice
        {
            "id": "4",
            "amount": 718.00,
            "date": "2026-02-30",
            "note": "Payment for INV-999",
        },  # Invalid date, should be skipped
    ]
    mocker.patch.object(
        MockBankAPIServer,
        "get_transactions",
        side_effect=[
            MockHttpResponse(status_code=500),
            MockHttpResponse(status_code=200, data=transactions),
        ],
    )
    # mock_server_inst = mock_server_class.return_value
    # mock_server_inst.get_transactions.side_effect = [
    #     MockHttpResponse(status_code=500),
    #     MockHttpResponse(status_code=200, data=transactions),
    # ]

    return server


def test_custom_integration_pipeline(mocker, mock_csv_file, mock_bank_api_server):
    reconciliation = Reconciliation()
    report = reconciliation.generate_report()

    assert len(report.reconciled) == 1, "Expected 1 reconciled pair"
    assert report.reconciled[0][0].invoice_number == "INV-642"  # type: ignore

    assert len(report.unmatched_invoices) == 2, "Expected 2 unmatched invoices"

    unmatched_inv_nums = [invoice.invoice_number for invoice in report.unmatched_invoices]  # type: ignore
    assert "INV-987" in unmatched_inv_nums
    assert "INV-123" in unmatched_inv_nums

    assert len(report.unmatched_transactions) == 2, "Expected 2 unmatched transactions"

    unmatched_transaction_ids = [transaction.id for transaction in report.unmatched_transactions]  # type: ignore
    assert "2" in unmatched_transaction_ids
    assert "3" in unmatched_transaction_ids
