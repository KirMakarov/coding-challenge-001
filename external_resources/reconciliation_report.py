import csv
from dataclasses import dataclass
from pathlib import Path

from .bank import Transaction
from .invoice_data import Invoice

CSV_RECONCILIATION_REPORT_FIELD_NAMES = [
    "type",
    "date",
    "amount",
    "invoice_number",
    "transaction_id",
    "transaction_note",
]


@dataclass
class ReconciliationReport:
    reconciled: list[object]
    unmatched_invoices: list[object]
    unmatched_transactions: list[object]

    def print_report(self):
        print("\n" + "=" * 30)
        print("Reconciliation Report:")

        print(f"Total Reconciled: {len(self.reconciled)}")

        print(f"Unmatched Invoices: {len(self.unmatched_invoices)}")
        for idx, invoice in enumerate(self.unmatched_invoices, start=1):
            print(f"{idx} - unmatched Invoice: '{invoice}'")

        print(f"Unmatched Transactions: {len(self.unmatched_transactions)}")
        for idx, transaction in enumerate(self.unmatched_transactions, start=1):
            print(f"{idx} - unmatched Transaction: '{transaction}'")

        print("=" * 30 + "\n")

    def export_to_csv(self, file_path: Path | str):
        file_path = Path(file_path)
        with open(file_path, "w", newline="") as csvfile:

            writer = csv.DictWriter(
                csvfile, fieldnames=CSV_RECONCILIATION_REPORT_FIELD_NAMES
            )

            writer.writeheader()
            for invoice in self.unmatched_invoices:
                if isinstance(invoice, Invoice):
                    writer.writerow(
                        {
                            "type": "unmatched_invoice",
                            "invoice_number": invoice.invoice_number,
                            "amount": invoice.total_amount,
                            "date": invoice.due_date,
                            "transaction_id": "",
                            "transaction_note": "",
                        }
                    )
            for transaction in self.unmatched_transactions:
                if isinstance(transaction, Transaction):
                    writer.writerow(
                        {
                            "type": "unmatched_transaction",
                            "invoice_number": "",
                            "amount": transaction.amount,
                            "date": transaction.date,
                            "transaction_id": transaction.id,
                            "transaction_note": transaction.note,
                        }
                    )
