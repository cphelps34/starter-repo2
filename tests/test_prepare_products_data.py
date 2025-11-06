import csv
import sys
import os

# Ensure `src/` is on sys.path so tests can import the package locally.
tests_dir = os.path.dirname(__file__)
repo_root = os.path.abspath(os.path.join(tests_dir, ".."))
src_dir = os.path.join(repo_root, "src")
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from starter_repo2.prepare_products_data import prepare_products_data


def test_prepare_products_data(tmp_path):
    input_file = tmp_path / "products_in.csv"
    output_file = tmp_path / "products_out.csv"

    with input_file.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Product ID", "Product Name", "Price"])
        writer.writerow(["p-001", " Widget ", " 9.99 "])
        writer.writerow(["", "", ""])  # blank row

    prepare_products_data(str(input_file), str(output_file))

    assert output_file.exists()
    with output_file.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        assert reader.fieldnames == ["product_id", "product_name", "price"]
        rows = list(reader)
        assert len(rows) == 1
        assert rows[0]["product_id"] == "p-001"
        assert rows[0]["product_name"] == "Widget"
