#!/usr/bin/env python3
import argparse
import re
import sys
from typing import Pattern, Sequence

# Regex pattern to match
CPG_FORBIDDEN_PATTERN = re.compile(r'[CX]PG\d+')


def check_file(file_path: str, extra_patterns: list[Pattern[str]]) -> bool:
    """Check if the given file contains the forbidden pattern."""
    patterns: list[Pattern[str]] = [CPG_FORBIDDEN_PATTERN, *extra_patterns]
    has_forbidden_pattern = False
    has_printed_header = False
    try:
        with open(file_path) as file:
            for line_number, line in enumerate(file):
                for pattern in patterns:
                    if pattern.search(line):
                        has_forbidden_pattern = True
                        if not has_printed_header:
                            print(f'{file_path}:')
                            has_printed_header = True
                        print(
                            f'  {line_number+1}: Has pattern "{pattern.pattern}": {line.strip()}',
                        )
    except OSError:
        # Ignore files that can't be opened (e.g., deleted files)
        pass

    if has_forbidden_pattern:
        # Print a blank line to separate output from different files
        print()

    return has_forbidden_pattern


def main(argv: Sequence[str] | None = None):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--extra-pattern',
        action='append',
        help='Extra pattern to check for',
    )
    parser.add_argument('filenames', nargs='*', help='Filenames to fix')
    args = parser.parse_args(argv)

    extra_patterns: list[Pattern[str]] = (
        [re.compile(e) for e in args.extra_pattern] if args.extra_pattern else []
    )

    has_error = False
    for file in args.filenames:
        if check_file(file, extra_patterns=extra_patterns):
            has_error = True

    sys.exit(1 if has_error else 0)


if __name__ == "__main__":
    main()
