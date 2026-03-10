from pathlib import Path

from reconciliation import Reconciliation
from utils.logger import get_logger

logger = get_logger(__name__)


def main():
    try:
        output_path = Path.cwd() / "reconciliation_report.csv"
        reconciliation = Reconciliation()
        report = reconciliation.generate_report()
        report.print_report()
        report.export_to_csv(output_path)

    except Exception as e:
        logger.error(f"An error occurred: {e}", exc_info=True)


if __name__ == "__main__":
    main()
