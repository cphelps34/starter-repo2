import csv
import os
import statistics
from datetime import datetime
from typing import Dict, List

from analytics_project.data_prep.data_scrubber import (
    clean_string,
)
from analytics_project.data_prep.data_scrubber import (
    handle_missing_values as handle_missing_values_generic,
)
from analytics_project.data_prep.data_scrubber import (
    remove_duplicates as remove_duplicates_generic,
)
from analytics_project.data_prep.data_scrubber import (
    remove_outliers as remove_outliers_generic,
)
from analytics_project.data_prep.data_scrubber import (
    standardize_date,
    standardize_id,
    standardize_numeric,
)


def handle_missing_values(data: List[Dict]) -> List[Dict]:
    """Delegate missing-value handling to the shared utility with sensible defaults."""
    defaults = {
        "CustomerID": "000000",
        "ProductID": "0000",
        "StoreID": "000",
        "CampaignID": "0",
        "SaleAmount": "0.00",
        "Expenses": "0.00",
        "Coast": "Unknown",
        "PaymentMethod": "Unknown",
        "Discount": "0.00",
        "Status": "Completed",
    }

    required = ["TransactionID"]
    return handle_missing_values_generic(data, defaults, required)


def validate_relationships(data: List[Dict]) -> List[Dict]:
    """Validate that CustomerID and ProductID exist in cleaned reference data.

    Falls back to trusting sales file IDs if reference files are missing.
    """
    valid_data = []
    initial_count = len(data)
    print(f"Initial record count before validation: {initial_count}")

    def std_cust(cid: str) -> str:
        return standardize_id(cid, width=6)

    def std_prod(pid: str) -> str:
        return standardize_id(pid, width=4)

    # Load reference customer ids
    customer_ids = set()
    cust_ref = os.path.join("Data", "Processed", "customers_data_cleaned.csv")
    try:
        with open(cust_ref, "r", newline="") as f:
            reader = csv.DictReader(f)
            customer_ids = {std_cust(r.get("CustomerID")) for r in reader}
            print(f"Found {len(customer_ids)} valid customer IDs")
    except FileNotFoundError:
        print(
            "Warning: Cleaned customers data not found. Skipping customer validation."
        )
        customer_ids = {std_cust(r.get("CustomerID")) for r in data}
        print(f"Using {len(customer_ids)} customer IDs from sales data")

    # Load reference product ids
    product_ids = set()
    prod_ref = os.path.join("Data", "Processed", "products_data_cleaned.csv")
    try:
        with open(prod_ref, "r", newline="") as f:
            reader = csv.DictReader(f)
            product_ids = {std_prod(r.get("ProductID")) for r in reader}
            print(f"Found {len(product_ids)} valid product IDs")
    except FileNotFoundError:
        print("Warning: Cleaned products data not found. Skipping product validation.")
        product_ids = {std_prod(r.get("ProductID")) for r in data}
        print(f"Using {len(product_ids)} product IDs from sales data")

    print("\nSample standardized customer IDs:", list(sorted(customer_ids))[:5])
    print("Sample standardized product IDs:", list(sorted(product_ids))[:5])

    invalid_customers = set()
    invalid_products = set()

    for row in data:
        std_c = std_cust(row.get("CustomerID"))
        std_p = std_prod(row.get("ProductID"))

        ok = True
        if std_c not in customer_ids:
            invalid_customers.add(std_c)
            ok = False
        if std_p not in product_ids:
            invalid_products.add(std_p)
            ok = False

        if ok:
            valid_data.append(row)

    if invalid_customers:
        print("\nInvalid Customer IDs found (standardized):")
        print(
            ", ".join(sorted(list(invalid_customers))[:10]),
            "..." if len(invalid_customers) > 10 else "",
        )

    if invalid_products:
        print("\nInvalid Product IDs found (standardized):")
        print(
            ", ".join(sorted(list(invalid_products))[:10]),
            "..." if len(invalid_products) > 10 else "",
        )

    print(
        f"\nValid records after validation: {len(valid_data)} ({len(valid_data)/initial_count*100:.1f}%)"
    )
    return valid_data


def remove_outliers(data: List[Dict]) -> List[Dict]:
    """Remove outliers from sales amount and expenses using shared utility."""
    cleaned = data
    for field in ["SaleAmount", "Expenses"]:
        # use IQR and ensure non-negative floor inside the scrubber via min_value
        cleaned = remove_outliers_generic(cleaned, field, method="iqr", threshold=1.5)
    return cleaned


def standardize_format(data: List[Dict]) -> List[Dict]:
    """Standardize fields using shared scrubber helpers."""
    standardized = []
    for row in data:
        r = {}
        # IDs
        r["TransactionID"] = standardize_id(row.get("TransactionID"), width=6)
        r["CustomerID"] = standardize_id(row.get("CustomerID"), width=6)
        r["ProductID"] = standardize_id(row.get("ProductID"), width=4)

        # Dates
        r["SaleDate"] = standardize_date(row.get("SaleDate"))

        # Numerics
        r["SaleAmount"] = standardize_numeric(
            row.get("SaleAmount"), default=0.0, min_value=0.0, decimals=2
        )
        r["Expenses"] = standardize_numeric(
            row.get("Expenses"), default=0.0, min_value=0.0, decimals=2
        )

        # Other small fields
        r["Coast"] = clean_string(row.get("Coast"), default="Unknown")
        r["StoreID"] = standardize_id(row.get("StoreID"), width=3)
        r["CampaignID"] = standardize_numeric(
            row.get("CampaignID"), default=0.0, decimals=0
        )

        # Preserve any additional fields present in the input
        for key, val in row.items():
            if key in r:
                continue
            r[key] = val if val is not None else ""

        standardized.append(r)

    return standardized


def remove_duplicates(data: List[Dict]) -> List[Dict]:
    """Remove duplicates using the shared utility keyed on TransactionID."""
    return remove_duplicates_generic(data, "TransactionID")


def generate_summary(data: List[Dict]) -> None:
    """Print a concise summary of the cleaned sales data (keeps same metrics)."""
    print("\nSales Data Cleaning Summary:")
    print("=" * 50)

    print(f"Total sales records processed: {len(data)}")

    dates = [datetime.strptime(row["SaleDate"], "%Y-%m-%d") for row in data]
    print("\nDate Range:")
    print(f"  Earliest Sale: {min(dates).strftime('%Y-%m-%d')}")
    print(f"  Latest Sale: {max(dates).strftime('%Y-%m-%d')}")

    coasts = {}
    for row in data:
        coast = row.get("Coast", "Unknown")
        coasts[coast] = coasts.get(coast, 0) + 1

    print("\nCoast Distribution:")
    for coast, count in sorted(coasts.items()):
        print(f"  {coast}: {count} sales ({count/len(data)*100:.1f}%)")

    stores = {}
    for row in data:
        store = row.get("StoreID", "000")
        stores[store] = stores.get(store, 0) + 1

    print("\nStore Distribution:")
    for store, count in sorted(stores.items()):
        print(f"  Store {store}: {count} sales ({count/len(data)*100:.1f}%)")

    campaigns = {}
    for row in data:
        campaign = row.get("CampaignID", "0")
        campaigns[campaign] = campaigns.get(campaign, 0) + 1

    print("\nCampaign Distribution:")
    for campaign, count in sorted(campaigns.items()):
        print(f"  Campaign {campaign}: {count} sales ({count/len(data)*100:.1f}%)")

    amounts = [float(row["SaleAmount"]) for row in data]
    print("\nSales Amount Statistics:")
    print(f"  Average Amount: ${statistics.mean(amounts):.2f}")
    print(f"  Median Amount: ${statistics.median(amounts):.2f}")
    print(f"  Total Sales: ${sum(amounts):.2f}")
    print(f"  Min Amount: ${min(amounts):.2f}")
    print(f"  Max Amount: ${max(amounts):.2f}")

    expenses = [float(row["Expenses"]) for row in data]
    print("\nExpenses Statistics:")
    print(f"  Average Expenses: ${statistics.mean(expenses):.2f}")
    print(f"  Median Expenses: ${statistics.median(expenses):.2f}")
    print(f"  Total Expenses: ${sum(expenses):.2f}")
    print(f"  Min Expenses: ${min(expenses):.2f}")
    print(f"  Max Expenses: ${max(expenses):.2f}")

    print("=" * 50)


def process_sales_data(input_file: str, output_file: str) -> List[Dict]:
    """Top-level runner to process sales CSV file and write cleaned data."""
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"Input file not found: {input_file}")

    with open(input_file, mode="r", newline="") as f:
        reader = csv.DictReader(f)
        sales = list(reader)

    print(f"Loaded {len(sales)} sales records.")

    cleaned = handle_missing_values(sales)
    cleaned = validate_relationships(cleaned)
    cleaned = remove_outliers(cleaned)
    cleaned = standardize_format(cleaned)
    cleaned = remove_duplicates(cleaned)

    # Ensure output directory exists
    out_dir = os.path.dirname(os.path.abspath(output_file))
    os.makedirs(out_dir, exist_ok=True)

    with open(output_file, mode="w", newline="") as f:
        if cleaned:
            fieldnames = cleaned[0].keys()
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(cleaned)

    print(f"\nCleaned data saved to: {output_file}")
    return cleaned


if __name__ == "__main__":
    in_file = os.path.join("Data", "Raw", "sales_data.csv")
    out_file = os.path.join("Data", "Processed", "sales_data_cleaned.csv")
    cleaned = process_sales_data(in_file, out_file)
    generate_summary(cleaned)
