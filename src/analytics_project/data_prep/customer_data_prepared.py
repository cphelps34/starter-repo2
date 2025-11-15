"""
Customer Data Preparation Module

This module handles the cleaning and standardization of customer data.
It processes raw customer data from CSV files, handles missing values,
removes outliers, and standardizes data formats.
"""

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
    standardize_date,
    standardize_id,
    standardize_numeric,
)


def handle_missing_values(data: List[Dict]) -> List[Dict]:
    """Handle missing values in the customer data."""
    # Define defaults for customer data
    defaults = {
        "Age": "30",
        "Gender": "Unknown",
        "Location": "Unknown",
        "MembershipLevel": "Basic",
        "Region": "Unknown",
        "Division": "General",
    }

    # CustomerID is required
    required_fields = ["CustomerID"]

    # Skip rows with too many missing values (more than 50%)
    filtered_data = [
        row
        for row in data
        if sum(1 for v in row.values() if v in (None, "", "?")) <= len(row) / 2
    ]

    return handle_missing_values_generic(filtered_data, defaults, required_fields)


def remove_outliers(data: List[Dict]) -> List[Dict]:
    """Remove outliers from numeric fields using IQR method."""
    # Process each numeric field in sequence
    cleaned = data
    for field in ["Age", "PurchaseAmount"]:
        if field in data[0]:
            cleaned = remove_outliers_generic(
                cleaned, field, method="iqr", threshold=1.5
            )
    return cleaned


def standardize_format(data: List[Dict]) -> List[Dict]:
    """Standardize data formats."""
    standardized_data = []

    for row in data:
        standardized_row = row.copy()

        # Standardize CustomerID format
        if "CustomerID" in row:
            standardized_row["CustomerID"] = standardize_id(
                row["CustomerID"], prefix="CUST"
            )

        # Clean and standardize text fields
        text_fields = ["Gender", "Location", "MembershipLevel", "Region", "Division"]
        for field in text_fields:
            if field in row:
                standardized_row[field] = clean_string(row[field])

        # Standardize numeric fields
        if "Age" in row:
            standardized_row["Age"] = standardize_numeric(row["Age"], decimals=0)
        if "PurchaseAmount" in row:
            standardized_row["PurchaseAmount"] = standardize_numeric(
                row["PurchaseAmount"]
            )

        # Add any date fields that need standardization
        if "JoinDate" in row:
            standardized_row["JoinDate"] = standardize_date(row["JoinDate"])

        standardized_data.append(standardized_row)

    return standardized_data


def process_customer_data(input_file: str, output_file: str) -> List[Dict]:
    """Process customer data from input file and write cleaned data to output file.

    Args:
        input_file (str): Path to input CSV file
        output_file (str): Path to output CSV file

    Returns:
        List[Dict]: List of cleaned customer records

    Raises:
        FileNotFoundError: If input file cannot be found
        csv.Error: If CSV data is invalid
    """
    # Ensure the input file exists
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"Input file not found: {input_file}")
    # Read the CSV file
    with open(input_file, mode="r") as file:
        csv_reader = csv.DictReader(file)
        customers_data = list(csv_reader)

    if not customers_data:
        print("Warning: No data found in input file")
        return []

    # Clean the data
    print("Processing customer data...")
    cleaned_data = handle_missing_values(customers_data)
    print(f"After handling missing values: {len(cleaned_data)} records")

    cleaned_data = remove_outliers(cleaned_data)
    print(f"After removing outliers: {len(cleaned_data)} records")

    cleaned_data = standardize_format(cleaned_data)
    print(f"After standardization: {len(cleaned_data)} records")

    # Write the cleaned data to a new CSV file
    with open(output_file, mode="w", newline="") as file:
        fieldnames = cleaned_data[0].keys()
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(cleaned_data)

    print(f"\nCleaned data written to {output_file}")
    return cleaned_data


def main():
    """Main function to process customer data."""
    try:
        # Ensure output directory exists
        output_dir = os.path.dirname(os.path.abspath("Data/Processed"))
        if not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)

        # Path to the raw customers data file
        input_file = "Data/Raw/customers_data.csv"
        output_file = "Data/Processed/customers_data_cleaned.csv"

        # Process the data and generate summary
        if clean_data := process_customer_data(input_file, output_file):
            generate_summary(clean_data)
            print(f"\nData cleaning completed. Processed {len(clean_data)} records.")
        else:
            print("Error: No data was processed")

    except FileNotFoundError as e:
        print(f"Error: Could not find file - {e}")
    except csv.Error as e:
        print(f"Error: Invalid CSV data - {e}")
    except Exception as e:
        print(f"Error: An unexpected error occurred - {e}")


def generate_summary(data: List[Dict]) -> None:
    """Generate and print a summary of the cleaned data."""
    print("\nData Cleaning Summary:")
    print("=" * 50)

    # Record counts
    print(f"Total records processed: {len(data)}")

    # Analyze regions
    if "Region" in data[0]:
        regions: Dict[str, int] = {}
        for row in data:
            region = row["Region"]
            regions[region] = regions.get(region, 0) + 1
        print("\nRegion Distribution:")
        for region, count in sorted(regions.items()):
            print(f"  {region}: {count} records ({count/len(data)*100:.1f}%)")

    # Analyze divisions
    if "Division" in data[0]:
        divisions: Dict[str, int] = {}
        for row in data:
            div = row["Division"]
            divisions[div] = divisions.get(div, 0) + 1
        print("\nDivision Distribution:")
        for div, count in sorted(divisions.items()):
            print(f"  {div}: {count} records ({count/len(data)*100:.1f}%)")

    # Age statistics
    if "Age" in data[0]:
        ages = [int(row["Age"]) for row in data if "Age" in row]
        print("\nAge Statistics:")
        print(f"  Average Age: {statistics.mean(ages):.1f} years")
        print(f"  Median Age: {statistics.median(ages):.1f} years")
        print(f"  Min Age: {min(ages)} years")
        print(f"  Max Age: {max(ages)} years")

    # Join date analysis
    if "JoinDate" in data[0]:
        years: Dict[str, int] = {}
        for row in data:
            year = row["JoinDate"].split("/")[-1]
            years[year] = years.get(year, 0) + 1
        print("\nJoin Year Distribution:")
        for year, count in sorted(years.items()):
            print(f"  {year}: {count} records ({count/len(data)*100:.1f}%)")

    print("\nData Quality:")
    complete_records = sum(
        1 for row in data if not any(v is None for v in row.values())
    )
    print(
        f"  Complete records: {complete_records} ({complete_records/len(data)*100:.1f}%)"
    )
    print(f"  Records with defaults: {len(data) - complete_records}")

    print("=" * 50)

if __name__ == "__main__":
    main()
