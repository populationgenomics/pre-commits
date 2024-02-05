#!/usr/bin/env python3
import argparse
import os
import re
import sys
from typing import Pattern, Sequence

# Regex pattern to match
CPG_FORBIDDEN_PATTERN = re.compile(r'[CX]PG\d+')
# only want to scan certain file types

PROGRAMMING_LANGUAGES = {
    '.c',
    '.c++',
    '.cc',
    '.clj',
    '.cljc',
    '.cljs',
    '.cpp',
    '.cs',
    '.css',
    '.dart',
    '.edn',
    '.fs',
    '.fsi',
    '.fsscript',
    '.fsx',
    '.go',
    '.gradle',
    '.groovy',
    '.h',
    '.h++',
    '.hh',
    '.hpp',
    '.html',
    '.java',
    '.js',
    '.jsx',
    '.kt',
    '.kts',
    '.m',
    '.mm',
    '.php',
    '.pl',
    '.pm',
    '.py',
    '.rb',
    '.rs',
    '.rst',
    '.scala',
    '.sh',
    '.swift',
    '.tcl',
    '.ts',
    '.tsx',
    '.vue',
    '.xml',
}
BIOINF_FILE_FORMATS = {
    '.bed',
    '.fasta',
    '.fastq',
    '.gff',
    '.gff3',
    '.gtf',
    '.sam',
    '.vcf',
}
TEXT_FILE_EXTENSIONS = {
    '.csv',
    '.tsv',
    '.json',
    '.md',
    '.rst',
    '.toml',
    '.txt',
    '.yaml',
    '.yml',
}

ALL_TEXT_FILE_EXTENSIONS = (
    PROGRAMMING_LANGUAGES | BIOINF_FILE_FORMATS | TEXT_FILE_EXTENSIONS
)


def should_check_file(
    file_path: str,
    ignore_filename_format_patterns: list[Pattern[str]],
) -> bool:
    if ignore_filename_format_patterns:
        for pattern in ignore_filename_format_patterns:
            if pattern.search(file_path):
                return False

    # we don't have any whitelisted file extensions with multiple components
    # (eg: .tar.gz) so we can just use the last component of the file path
    file_extension = os.path.splitext(file_path)[1]

    # we'll check if there is NO file extension
    if file_extension and file_extension not in ALL_TEXT_FILE_EXTENSIONS:
        return False

    return True


def check_file(
    file_path: str,
    extra_patterns: list[Pattern[str]],
    ignore_filename_format_patterns: list[Pattern[str]],
) -> bool:
    """Check if the given file contains the forbidden pattern."""
    patterns: list[Pattern[str]] = [CPG_FORBIDDEN_PATTERN, *extra_patterns]

    if not should_check_file(file_path, ignore_filename_format_patterns):
        return False

    lines_to_print = []

    try:
        with open(file_path) as file:
            for line_number, line in enumerate(file):
                for pattern in patterns:
                    if pattern.search(line):
                        lines_to_print.append(
                            f'  {line_number+1}: Has pattern "{pattern.pattern}": {line.strip()}',
                        )
    except (OSError, UnicodeDecodeError):
        # Ignore files that can't be opened (e.g., deleted files)
        # or files that can't be decoded (e.g., binary files)
        return False

    if not lines_to_print:
        return False

    m = f'{file_path}:\n' + '\n'.join(lines_to_print) + "\n"
    print(m)
    return True


def main(argv: Sequence[str] | None = None):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--extra-pattern',
        action='append',
        help='Extra sample pattern to check for',
    )
    parser.add_argument(
        '--ignore-filename-format',
        action='append',
        help='Ignore files whose name match the given pattern',
    )
    parser.add_argument('filenames', nargs='*', help='Filenames to fix')
    args = parser.parse_args(argv)

    extra_patterns: list[Pattern[str]] = (
        [re.compile(e) for e in args.extra_pattern] if args.extra_pattern else []
    )

    ignore_filename_format_patterns: list[Pattern[str]] = (
        [re.compile(e) for e in args.ignore_filename_format]
        if args.ignore_filename_format
        else []
    )

    has_error = False
    for file in args.filenames:
        if check_file(
            file,
            extra_patterns=extra_patterns,
            ignore_filename_format_patterns=ignore_filename_format_patterns,
        ):
            has_error = True

    sys.exit(1 if has_error else 0)


if __name__ == "__main__":
    main()
