"""Utilities to prepare customers CSV data.

This module provides a small, dependency-free CSV cleaner used for the
starter repository. It normalizes header names (lowercase, underscores)
and strips whitespace from values. Empty rows (all values blank) are
removed.
"""

import csv
from pathlib import Path


def _normalize_header(name: str) -> str:
    if name is None:
        return ""
    return name.strip().lower().replace(" ", "_")


def prepare_customers_data(input_path, output_path):
    """Read a CSV from `input_path`, clean it, and write to `output_path`.

    Cleaning steps:
    - Normalize header names to lowercase with underscores instead of spaces
    - Strip leading/trailing whitespace from all values
    - Drop rows where all values are empty

    Returns the Path to the written output file.
    """
    input_path = Path(input_path)
    output_path = Path(output_path)

    with input_path.open("r", newline="", encoding="utf-8") as fin:
        reader = csv.DictReader(fin)
        original_fieldnames = reader.fieldnames or []
        fieldnames = [_normalize_header(fn) for fn in original_fieldnames]

        cleaned_rows = []
        for raw_row in reader:
            # Normalize keys and strip values
            row = {}
            for k, v in raw_row.items():
                nk = _normalize_header(k)
                row[nk] = v.strip() if v is not None else ""
            # keep row if any value non-empty
            if any(value != "" for value in row.values()):
                cleaned_rows.append(row)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as fout:
        writer = csv.DictWriter(fout, fieldnames=fieldnames)
        writer.writeheader()
        for r in cleaned_rows:
            # Ensure all expected fields are present
            out_row = {fn: r.get(fn, "") for fn in fieldnames}
            writer.writerow(out_row)

    return output_path


if __name__ == "__main__":
    import argparse

    p = argparse.ArgumentParser(description="Prepare customers CSV data")
    p.add_argument("input", help="Path to input CSV file")
    p.add_argument("output", help="Path where cleaned CSV will be written")
    args = p.parse_args()
    prepare_customers_data(args.input, args.output)
