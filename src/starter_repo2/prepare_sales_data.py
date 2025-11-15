"""Utilities to prepare sales CSV data.

This module mirrors the simple cleaning behaviour used for customers and
products: normalize headers to lowercase with underscores, strip whitespace
from values, and drop fully-empty rows.
"""

import csv
from pathlib import Path


def _normalize_header(name: str) -> str:
    if name is None:
        return ""
    return name.strip().lower().replace(" ", "_")


def prepare_sales_data(input_path, output_path):
    """Clean a sales CSV and write cleaned file to `output_path`.

    Behaviour:
    - Normalize header names (lowercase, underscores)
    - Strip whitespace from all values
    - Remove rows where all values are empty

    Returns the output path.
    """
    input_path = Path(input_path)
    output_path = Path(output_path)

    with input_path.open("r", newline="", encoding="utf-8") as fin:
        reader = csv.DictReader(fin)
        original_fieldnames = reader.fieldnames or []
        fieldnames = [_normalize_header(fn) for fn in original_fieldnames]

        cleaned_rows = []
        for raw_row in reader:
            row = {}
            for k, v in raw_row.items():
                nk = _normalize_header(k)
                row[nk] = v.strip() if v is not None else ""
            if any(value != "" for value in row.values()):
                cleaned_rows.append(row)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as fout:
        writer = csv.DictWriter(fout, fieldnames=fieldnames)
        writer.writeheader()
        for r in cleaned_rows:
            out_row = {fn: r.get(fn, "") for fn in fieldnames}
            writer.writerow(out_row)

    return output_path


if __name__ == "__main__":
    import argparse

    p = argparse.ArgumentParser(description="Prepare sales CSV data")
    p.add_argument("input", help="Path to input CSV file")
    p.add_argument("output", help="Path where cleaned CSV will be written")
    args = p.parse_args()
    prepare_sales_data(args.input, args.output)
