import argparse
import os
import sys
from runner import run_recipe
from logger import init_logger


def parse_args():
    parser = argparse.ArgumentParser(description='Recipe Executor CLI')
    parser.add_argument('recipe', type=str, help='Path to the recipe markdown file')
    parser.add_argument('--root', type=str, default='output', help='Output root directory')
    parser.add_argument('--log-dir', type=str, default='logs', help='Directory for log files')
    return parser.parse_args()


def clear_logs(log_dir):
    # Ensure log directory exists
    os.makedirs(log_dir, exist_ok=True)
    for log_file in ['debug.log', 'info.log', 'error.log']:
        with open(os.path.join(log_dir, log_file), 'w') as f:
            f.truncate(0)


if __name__ == '__main__':
    args = parse_args()
    clear_logs(args.log_dir)
    logger = init_logger(args.log_dir)
    try:
        run_recipe(recipe_path=args.recipe, output_root=args.root, log_dir=args.log_dir, logger=logger)
    except Exception as e:
        logger.error(f'Fatal error: {e}', exc_info=True)
        sys.exit(1)
