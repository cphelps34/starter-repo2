import csv
import os
import statistics
from typing import Dict, List

from analytics_project.data_prep.data_scrubber import (
    clean_string,
)
from analytics_project.data_prep.data_scrubber import (
    handle_missing_values as handle_missing_values_generic,
)
from analytics_project.data_prep.data_scrubber import (
    remove_outliers as remove_outliers_generic,
)
from analytics_project.data_prep.data_scrubber import (
    standardize_id,
    standardize_numeric,
)


def handle_missing_values(data: List[Dict]) -> List[Dict]:
    """Handle missing values in the product data."""
    # Define defaults for product data
    defaults = {
        "Category": "Uncategorized",
        "UnitPrice": "0.00",
        "Model": "1",
        "Branch": "Main",
    }

    required_fields = ["ProductID", "ProductName"]
    return handle_missing_values_generic(data, defaults, required_fields)


def remove_outliers(data: List[Dict]) -> List[Dict]:
    """Remove price outliers using IQR method."""
    return remove_outliers_generic(data, "UnitPrice", method="iqr", threshold=1.5)


def standardize_format(data: List[Dict]) -> List[Dict]:
    """Standardize data formats."""
    standardized_data = []

    # Define category and branch mappings
    category_mapping = {
        "electronics": "Electronics",
        "clothing": "Clothing",
        "home": "Home",
        "office": "Office",
    }

    branch_mapping = {
        "la": "Los Angeles",
        "l.a.": "Los Angeles",
        "ny": "New York",
        "n.y.": "New York",
    }

    for row in data:
        std_row = {}

        for key, value in row.items():
            if key == "ProductID":
                std_row[key] = standardize_id(value, width=4)
            elif key == "ProductName":
                std_row[key] = clean_string(value).replace("-", " ")
            elif key == "Category":
                # Use clean_string but apply category mapping
                cleaned = clean_string(value).lower()
                std_row[key] = category_mapping.get(cleaned, clean_string(value))
            elif key == "UnitPrice":
                std_row[key] = standardize_numeric(value, min_value=0)
            elif key == "Model":
                std_row[key] = standardize_id(value, width=1)
            elif key == "Branch":
                # Use clean_string but apply branch mapping
                cleaned = clean_string(value).lower()
                std_row[key] = branch_mapping.get(cleaned, clean_string(value))
            else:
                std_row[key] = clean_string(value)

        standardized_data.append(std_row)

    return standardized_data


def generate_summary(data: List[Dict]) -> None:
    """Generate and print a summary of the cleaned data."""
    print("\nProduct Data Cleaning Summary:")
    print("=" * 50)

    # Record counts
    print(f"Total products processed: {len(data)}")

    # Category distribution
    categories = {}
    for row in data:
        cat = row["Category"]
        categories[cat] = categories.get(cat, 0) + 1

    print("\nCategory Distribution:")
    for cat, count in sorted(categories.items()):
        print(f"  {cat}: {count} products ({count/len(data)*100:.1f}%)")

    # Price analysis
    prices = [float(row["UnitPrice"]) for row in data]
    print("\nPrice Statistics:")
    print(f"  Average Price: ${statistics.mean(prices):.2f}")
    print(f"  Median Price: ${statistics.median(prices):.2f}")
    print(f"  Price Range: ${min(prices):.2f} - ${max(prices):.2f}")

    # Branch distribution
    branches = {}
    for row in data:
        branch = row["Branch"]
        branches[branch] = branches.get(branch, 0) + 1

    print("\nBranch Distribution:")
    for branch, count in sorted(branches.items()):
        print(f"  {branch}: {count} products ({count/len(data)*100:.1f}%)")

    print("=" * 50)




def process_product_data(input_file: str, output_file: str) -> List[Dict]:
    """Process product data from input file and write cleaned data to output file."""
    with open(input_file, mode="r", newline="") as file:
        csv_reader = csv.DictReader(file)
        products_data = list(csv_reader)

    print(f"Loaded {len(products_data)} product records.")

    # Clean the data
    print("Cleaning data...")
    cleaned_data = handle_missing_values(products_data)
    cleaned_data = remove_outliers(cleaned_data)
    cleaned_data = standardize_format(cleaned_data)

    # Ensure output directory exists
    out_dir = os.path.dirname(os.path.abspath(output_file))
    os.makedirs(out_dir, exist_ok=True)

    # Write the cleaned data to a new CSV file
    with open(output_file, mode="w", newline="") as file:
        if cleaned_data:
            fieldnames = cleaned_data[0].keys()
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(cleaned_data)

    print(f"\nCleaned data saved to: {output_file}")
    return cleaned_data


if __name__ == "__main__":
    in_file = os.path.join("Data", "Raw", "products_data.csv")
    out_file = os.path.join("Data", "Processed", "products_data_cleaned.csv")
    cleaned = process_product_data(in_file, out_file)
    generate_summary(cleaned)
