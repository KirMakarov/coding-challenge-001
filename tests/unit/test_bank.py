from datetime import date
from decimal import Decimal

import pytest
from external_resources.bank import BankAPIClient, Transaction
from external_resources.mock_bank_api import MockBankAPIServer, MockHttpResponse


@pytest.fixture
def bank_client():
    client = BankAPIClient()
    client._max_delay_seconds = 0  # Set to 0 to speed up tests
    return client


def test_transaction_create():
    tx = Transaction.create("1", 150.01, "2026-01-01", "Note")
    assert tx.amount == Decimal("150.01")
    assert tx.date == date(2026, 1, 1)


def test_fetch_transactions_success(bank_client, mocker):
    mock_response = MockHttpResponse(
        status_code=200,
        data=[
            {
                "id": "001",
                "amount": 50.00,
                "date": "2026-07-10",
                "note": "Payment for INV-001",
            }
        ],
    )
    mocker.patch.object(
        MockBankAPIServer, "get_transactions", return_value=mock_response
    )

    transactions = list(bank_client.fetch_transactions())

    assert len(transactions) == 1
    assert transactions[0].id == "001"


def test_fetch_transactions_unauthorized(bank_client, mocker):
    mocker.patch.object(
        MockBankAPIServer,
        "get_transactions",
        return_value=MockHttpResponse(status_code=401),
    )

    with pytest.raises(PermissionError):
        list(bank_client.fetch_transactions())


def test_fetch_transactions_retry_exhausted(bank_client, mocker):
    mock_fetch = mocker.patch.object(
        MockBankAPIServer,
        "get_transactions",
        return_value=MockHttpResponse(status_code=500),
    )

    with pytest.raises(ConnectionError):
        list(bank_client.fetch_transactions())

    assert mock_fetch.call_count == bank_client._max_retry_attempts


def test_fetch_transactions_none_data(bank_client, mocker):
    mocker.patch.object(
        MockBankAPIServer,
        "get_transactions",
        return_value=MockHttpResponse(status_code=200, data=None),
    )
    assert list(bank_client.fetch_transactions()) == []


def test_fetch_transactions_bad_data(bank_client, mocker):
    bad_data = [
        {"id": "1", "amount": "bad_amount", "date": "2026-01-01", "note": "note"},
        {"id": "2", "amount": "100", "date": "bad_date", "note": "note"},
    ]
    mocker.patch.object(
        MockBankAPIServer,
        "get_transactions",
        return_value=MockHttpResponse(status_code=200, data=bad_data),
    )
    assert list(bank_client.fetch_transactions()) == []


def test_request_with_retry_unknown_status(bank_client, mocker):
    mocker.patch.object(
        MockBankAPIServer,
        "get_transactions",
        return_value=MockHttpResponse(status_code=404),
    )
    with pytest.raises(ConnectionError, match="Status code: 404"):
        bank_client._request_with_retry(bank_client._fetch_transactions)
