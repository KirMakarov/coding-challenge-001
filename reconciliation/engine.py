from typing import Iterator

from external_resources.bank import BankAPIClient, Transaction
from external_resources.invoice_data import Invoice, extract_invoice_data
from external_resources.reconciliation_report import ReconciliationReport


class Reconciliation:
    _inv_number_prefix = "INV-"

    def __init__(self):
        self.bank_api_client = BankAPIClient()

    def generate_report(self) -> ReconciliationReport:
        transactions = self._fetch_bank_transactions()
        invoices = self._fetch_invoices()
        return self._match_transactions_and_invoices(transactions, invoices)

    def generate_and_print_report(self) -> None:
        report = self.generate_report()
        report.print_report()

    def _fetch_bank_transactions(self) -> Iterator[Transaction]:
        return self.bank_api_client.fetch_transactions()

    def _fetch_invoices(self) -> Iterator[Invoice]:
        return extract_invoice_data()

    def _match_transactions_and_invoices(
        self, transactions: Iterator[Transaction], invoices: Iterator[Invoice]
    ) -> ReconciliationReport:
        transaction_mapping_by_invoice, unmatched_transactions = (
            self._map_transactions_by_invoice_number(transactions)
        )

        unmatched_invoices = []
        reconciled = []

        for invoice in invoices:
            invoice_number = invoice.invoice_number
            matched_transaction = transaction_mapping_by_invoice.get(invoice_number)
            if self._are_transaction_and_invoice_equal(matched_transaction, invoice):
                reconciled.append((invoice, matched_transaction))
                del transaction_mapping_by_invoice[invoice_number]
            else:
                unmatched_invoices.append(invoice)

        unmatched_transactions.extend(transaction_mapping_by_invoice.values())

        return ReconciliationReport(
            reconciled=reconciled,
            unmatched_invoices=unmatched_invoices,
            unmatched_transactions=unmatched_transactions,
        )

    def _map_transactions_by_invoice_number(
        self, transactions: Iterator[Transaction]
    ) -> tuple[dict[str, Transaction], list[Transaction]]:
        transaction_map = {}
        unmatched_transactions = []

        for transaction in transactions:
            invoice_prefix_index = transaction.note.find(self._inv_number_prefix)
            if invoice_prefix_index != -1:
                invoice_number = transaction.note[invoice_prefix_index:].split()[0]
                transaction_map[invoice_number] = transaction
            else:
                unmatched_transactions.append(transaction)
        return transaction_map, unmatched_transactions

    @staticmethod
    def _are_transaction_and_invoice_equal(
        transaction: Transaction | None, invoice: Invoice
    ) -> bool:
        return (
            transaction is not None
            and transaction.date == invoice.due_date
            and transaction.amount == invoice.total_amount
        )
