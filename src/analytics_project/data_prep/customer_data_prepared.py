import csv
import statistics
from typing import List, Dict

def handle_missing_values(data: List[Dict]) -> List[Dict]:
    """Handle missing values in the customer data."""
    cleaned_data = []
    for row in data:
        # Replace empty strings with None
        row = {k: (None if v == '' else v) for k, v in row.items()}
        
        # Skip rows with too many missing values (more than 50%)
        if sum(1 for v in row.values() if v is None) > len(row) / 2:
            continue
            
        # Fill missing values with appropriate defaults
        if row['CustomerID'] is None:
            continue  # Skip rows with missing CustomerID
        
        # Fill other missing values with appropriate defaults
        defaults = {
            'Age': '30',
            'Gender': 'Unknown',
            'Location': 'Unknown',
            'MembershipLevel': 'Basic'
        }
        
        for field, default in defaults.items():
            if field in row and row[field] is None:
                row[field] = default
                
        cleaned_data.append(row)
    return cleaned_data

def remove_outliers(data: List[Dict]) -> List[Dict]:
    """Remove outliers from numeric fields using IQR method."""
    numeric_fields = ['Age', 'PurchaseAmount']
    cleaned_data = []
    
    for field in numeric_fields:
        if field not in data[0]:
            continue
            
        # Convert to float for numeric fields
        values = [float(row[field]) for row in data if row[field] is not None]
        
        # Calculate Q1, Q3 and IQR
        q1 = statistics.quantiles(values, n=4)[0]
        q3 = statistics.quantiles(values, n=4)[2]
        iqr = q3 - q1
        
        # Define outlier bounds
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        
        # Filter out outliers
        for row in data:
            if field in row and row[field] is not None:
                value = float(row[field])
                if lower_bound <= value <= upper_bound:
                    cleaned_data.append(row)
    
    return cleaned_data

def standardize_format(data: List[Dict]) -> List[Dict]:
    """Standardize data formats."""
    standardized_data = []
    
    # Define region mapping to handle variations
    region_mapping = {
        'EAST': 'East',
        'east': 'East',
        'WEST': 'West',
        'west': 'West',
        'NORTH': 'North',
        'north': 'North',
        'SOUTH': 'South',
        'south': 'South',
        'CENTRAL': 'Central',
        'central': 'Central',
        'south-west': 'Southwest',
        'SOUTH-WEST': 'Southwest',
        'south west': 'Southwest',
        'SOUTH WEST': 'Southwest'
    }
    
    for row in data:
        # Create a new standardized row
        std_row = {}
        
        for key, value in row.items():
            if value is None:
                std_row[key] = value
                continue
                
            # Standardize specific fields
            if key == 'CustomerID':
                std_row[key] = str(value).zfill(6)  # Ensure 6-digit ID
            elif key == 'Age':
                std_row[key] = str(int(float(value)))  # Convert to integer
            elif key == 'Region':
                # Clean up region value first
                cleaned_region = value.strip()
                # Use mapping if exists, otherwise title case the value
                std_row[key] = region_mapping.get(cleaned_region, cleaned_region.title())
            elif key == 'Division':
                std_row[key] = value.strip().title()  # Title case division
            elif key == 'Name':
                std_row[key] = ' '.join(word.capitalize() for word in value.strip().split())  # Proper name format
            else:
                std_row[key] = value
                
        standardized_data.append(std_row)
    
    return standardized_data

# Path to the raw customers data file
input_file = "../../../Data/Raw/customers_data.csv"
output_file = "../../../Data/Processed/customers_data_cleaned.csv"

# Read the CSV file
with open(input_file, mode='r') as file:
    csv_reader = csv.DictReader(file)
    customers_data = list(csv_reader)

# Clean the data
cleaned_data = handle_missing_values(customers_data)
cleaned_data = remove_outliers(cleaned_data)
cleaned_data = standardize_format(cleaned_data)

# Write the cleaned data to a new CSV file
with open(output_file, mode='w', newline='') as file:
    if cleaned_data:
        fieldnames = cleaned_data[0].keys()
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(cleaned_data)

def generate_summary(data: List[Dict]) -> None:
    """Generate and print a summary of the cleaned data."""
    print("\nData Cleaning Summary:")
    print("=" * 50)
    
    # Record counts
    print(f"Total records processed: {len(data)}")
    
    # Analyze regions
    if 'Region' in data[0]:
        regions = {}
        for row in data:
            region = row['Region']
            regions[region] = regions.get(region, 0) + 1
        print("\nRegion Distribution:")
        for region, count in sorted(regions.items()):
            print(f"  {region}: {count} records ({count/len(data)*100:.1f}%)")
    
    # Analyze divisions
    if 'Division' in data[0]:
        divisions = {}
        for row in data:
            div = row['Division']
            divisions[div] = divisions.get(div, 0) + 1
        print("\nDivision Distribution:")
        for div, count in sorted(divisions.items()):
            print(f"  {div}: {count} records ({count/len(data)*100:.1f}%)")
    
    # Age statistics
    if 'Age' in data[0]:
        ages = [int(row['Age']) for row in data if 'Age' in row]
        print("\nAge Statistics:")
        print(f"  Average Age: {statistics.mean(ages):.1f} years")
        print(f"  Median Age: {statistics.median(ages):.1f} years")
        print(f"  Min Age: {min(ages)} years")
        print(f"  Max Age: {max(ages)} years")
    
    # Join date analysis
    if 'JoinDate' in data[0]:
        years = {}
        for row in data:
            year = row['JoinDate'].split('/')[-1]
            years[year] = years.get(year, 0) + 1
        print("\nJoin Year Distribution:")
        for year, count in sorted(years.items()):
            print(f"  {year}: {count} records ({count/len(data)*100:.1f}%)")
    
    print("\nData Quality:")
    complete_records = sum(1 for row in data if not any(v is None for v in row.values()))
    print(f"  Complete records: {complete_records} ({complete_records/len(data)*100:.1f}%)")
    print(f"  Records with defaults: {len(data) - complete_records}")
    
    print("=" * 50)

# Generate and print summary
generate_summary(cleaned_data)
print(f"\nData cleaning completed. Processed {len(cleaned_data)} records.")