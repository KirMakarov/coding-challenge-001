import http
import itertools
import time
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from typing import Callable, Iterator

from utils.logger import get_logger

from .mock_bank_api import MockBankAPIServer, MockHttpResponse
from .secrets import MOCK_BANK_API_TOKENS

logger = get_logger(__name__)

@dataclass
class Transaction:
    id: str
    amount: Decimal
    date: date
    note: str

    @classmethod
    def create(
        cls,
        id: str,
        amount: str | Decimal | float | int,
        date: str | date,
        note: str,
    ):
        if not isinstance(amount, Decimal):
            amount = Decimal(str(amount))
        if isinstance(date, str):
            date = datetime.strptime(date, "%Y-%m-%d").date()
        return cls(id, amount=amount, date=date, note=note)
    
    def __repr__(self):
        return f"Transaction: id - {self.id}, amount - {self.amount}, date - {self.date}, note - {self.note}"


class BankAPIClient:
    _max_retry_attempts: int = 10
    _max_delay_seconds: int = 5
    _token: Iterator[str] | None = None
    _bank_api_client: MockBankAPIServer | None = None

    def fetch_transactions(self) -> Iterator[Transaction]:
        transactions_data = self._request_with_retry(self._fetch_transactions)
        if transactions_data is None:
            return
        for data in transactions_data:
            try:
                yield Transaction.create(**data)
            except (ValueError, InvalidOperation) as e:
                logger.error(f"Error creating Transaction from data: {data}. Error: {e}")

    def _get_auth_token(self):
        if not self._token:
            self._token = itertools.cycle(token for token in MOCK_BANK_API_TOKENS if token)
        return next(self._token)

    def _build_headers(self):
        return {"auth_token": self._get_auth_token()}

    def _fetch_transactions(self):
        if not self._bank_api_client:
            self._bank_api_client = MockBankAPIServer()

        request = {"Headers": self._build_headers()}

        return self._bank_api_client.get_transactions(request=request)

    def _request_with_retry(
        self, request_func: Callable[[], MockHttpResponse]
    ) -> list[dict] | None:
        retry_count = 0
        while retry_count < self._max_retry_attempts:
            retry_count += 1

            response = request_func()

            if response.status_code == http.HTTPStatus.OK:
                return response.json()
            elif response.status_code == http.HTTPStatus.UNAUTHORIZED:
                raise PermissionError(
                    "Unauthorized access to the bank API. Invalid auth token."
                )
            elif response.status_code == http.HTTPStatus.INTERNAL_SERVER_ERROR:
                logger.error(f"Attempt {retry_count} failed: {response.status_code}", exc_info=True)
                if retry_count >= self._max_retry_attempts:
                    raise ConnectionError(
                        "Bank API is currently unavailable. Please try again later."
                    )
                self._delay_before_retry(retry_count)
            else:
                raise ConnectionError(
                    f"Failed to fetch transactions from the bank API. Status code: {response.status_code}"
                )

    def _delay_before_retry(self, retry_count: int) -> None:
        delay = min(0.1 * retry_count, self._max_delay_seconds)
        time.sleep(delay)
