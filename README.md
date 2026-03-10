# Task Description
Candidate is requested to implement a reconciliation process with the following ETL steps:
1. Extract invoice data from a CSV file. The path to the CSV file is specified in `external_resources/invoice_data.py`.
2. Extract bank transaction data from a mock API endpoint. The API should be accessed via the `MockBankAPI` class defined in `external_resources/mock_bank_api.py`.
3. Produce a `ReconciliationReport` (defined in `external_resources/reconciliation_report.py`) by matching invoices with transactions based on criteria identified through data analysis.

Bonus points for:
- Generating a CSV report summarizing matched and unmatched records.

Notes:
- The implementation should be scalable to handle larger datasets (e.g., >100k records).
- Provide sufficient test coverage (unit and integration tests) to validate the reconciliation logic.
- Ensure proper error handling, enabling efficient debugging

# Reconciliation Processor Implementation

## Overview
This project implements a reconciliation process that extracts invoice data from a CSV file and bank transaction data from a mock API, then produces a reconciliation report by matching invoices with transactions. 

## Quick Start

1. Clone the repository
    ```bash
    git clone
    ```
2. Navigate to the project directory
    ```bash
    cd coding-challenge-001
    ```
3. Run the reconciliation process
    ```bash
    python main.py
    ```

## Setup and Execution Tests

1. Install virtual environment
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

2. Install dependencies
    ```bash
    pip install -r requirements.txt
    ```
3. Run tests
    Execute all tests in the `tests/` directory.
    ```bash
    pytest tests/
    ```

4. Run tests with coverage report
   Run tests and generate a terminal report showing coverage for `main.py` and the `external_resources` package.
    ```bash
    pytest tests/ --cov=main --cov=external_resources --cov-report=term-missing
    ```
