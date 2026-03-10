from reconciliation import Reconciliation
from utils.logger import get_logger

logger = get_logger(__name__)

def main():
    try:
        reconciliation = Reconciliation()
        reconciliation.generate_and_print_report()
    except Exception as e:
        logger.error(f"An error occurred: {e}", exc_info=True)


if __name__ == "__main__":
    main()
