import csv
import sys
import os

# Ensure `src/` is on sys.path so test can import the package when it's not
# installed in the environment (editable install). This keeps tests local and
# hermetic for development clones.
tests_dir = os.path.dirname(__file__)
repo_root = os.path.abspath(os.path.join(tests_dir, ".."))
src_dir = os.path.join(repo_root, "src")
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from starter_repo2.prepare_customers_data import prepare_customers_data


def test_prepare_customers_data(tmp_path):
    input_file = tmp_path / "in.csv"
    output_file = tmp_path / "out.csv"

    # Create a small CSV with spaces in header and a blank row
    with input_file.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Customer ID", "Name", "Email"])
        writer.writerow(["123", " Alice ", "alice@example.com"])
        writer.writerow(["", "", ""])  # blank row should be removed

    prepare_customers_data(str(input_file), str(output_file))

    assert output_file.exists()
    with output_file.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        # headers should be normalized
        assert reader.fieldnames == ["customer_id", "name", "email"]
        rows = list(reader)
        assert len(rows) == 1
        assert rows[0]["customer_id"] == "123"
        assert rows[0]["name"] == "Alice"
