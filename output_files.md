Scanning patterns: ['output']
Excluding patterns: ['.venv', 'node_modules', '.git', '__pycache__', '*.pyc']
Including patterns: []
Found 3 files.

=== File: output/main_module/auxiliary.py ===
def auxiliary():
	return 'Hello from Auxiliary!'



=== File: output/main_module/main.py ===
def main():
	print('Hello from Main!')



=== File: output/utility_module/utility_module.py ===
import logging


def get_logger():
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    return logger


def process_data(data):
    return data


