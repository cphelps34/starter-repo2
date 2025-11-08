import csv
import statistics
from typing import List, Dict

def handle_missing_values(data: List[Dict]) -> List[Dict]:
    """Handle missing values in the product data."""
    cleaned_data = []
    for row in data:
        # Replace empty strings with None
        row = {k: (None if v == '' else v) for k, v in row.items()}
        
        # Skip rows with too many missing values (more than 50%)
        if sum(1 for v in row.values() if v is None) > len(row) / 2:
            continue
            
        # Skip rows with missing critical fields
        if row['ProductID'] is None or row['ProductName'] is None:
            continue
            
        # Fill missing values with appropriate defaults
        defaults = {
            'Category': 'Uncategorized',
            'UnitPrice': '0.00',
            'Model': '1',
            'Branch': 'Main'
        }
        
        for field, default in defaults.items():
            if field in row and row[field] is None:
                row[field] = default
                
        cleaned_data.append(row)
    return cleaned_data

def remove_outliers(data: List[Dict]) -> List[Dict]:
    """Remove price outliers using IQR method."""
    cleaned_data = []
    
    # Convert prices to float for analysis
    prices = [float(row['UnitPrice']) for row in data if row['UnitPrice']]
    
    # Calculate Q1, Q3 and IQR for prices
    q1 = statistics.quantiles(prices, n=4)[0]
    q3 = statistics.quantiles(prices, n=4)[2]
    iqr = q3 - q1
    
    # Define outlier bounds
    lower_bound = max(0, q1 - 1.5 * iqr)  # Don't allow negative prices
    upper_bound = q3 + 1.5 * iqr
    
    # Filter out price outliers
    for row in data:
        if row['UnitPrice']:
            price = float(row['UnitPrice'])
            if lower_bound <= price <= upper_bound:
                cleaned_data.append(row)
    
    return cleaned_data

def standardize_format(data: List[Dict]) -> List[Dict]:
    """Standardize data formats."""
    standardized_data = []
    
    # Define category mapping for consistency
    category_mapping = {
        'electronics': 'Electronics',
        'ELECTRONICS': 'Electronics',
        'clothing': 'Clothing',
        'CLOTHING': 'Clothing',
        'home': 'Home',
        'HOME': 'Home',
        'office': 'Office',
        'OFFICE': 'Office'
    }
    
    # Define branch name standardization
    branch_mapping = {
        'LA': 'Los Angeles',
        'Ll': 'Los Angeles',
        'La': 'Los Angeles',
        'l.a.': 'Los Angeles',
        'L.A.': 'Los Angeles',
        'New York': 'New York',
        'NY': 'New York',
        'N.Y.': 'New York',
        'ny': 'New York',
        'Main': 'Main'
    }
    
    for row in data:
        std_row = {}
        
        for key, value in row.items():
            if value is None:
                std_row[key] = value
                continue
                
            if key == 'ProductID':
                # Ensure 4-digit product ID with leading zeros
                std_row[key] = str(int(value)).zfill(4)
            elif key == 'ProductName':
                # Convert hyphenated names to space-separated and proper case
                words = value.replace('-', ' ').strip().split()
                std_row[key] = ' '.join(word.capitalize() for word in words)
            elif key == 'Category':
                # Standardize category names
                std_row[key] = category_mapping.get(value.lower(), value.title())
            elif key == 'UnitPrice':
                # Format price to 2 decimal places
                std_row[key] = f"{float(value):.2f}"
            elif key == 'Model':
                # Ensure model is a single digit
                std_row[key] = str(int(value))
            elif key == 'Branch':
                # Standardize branch names
                clean_value = value.strip()
                # Try exact match first
                if clean_value in branch_mapping:
                    std_row[key] = branch_mapping[clean_value]
                else:
                    # Try case-insensitive match
                    matches = [v for k, v in branch_mapping.items() 
                             if k.lower() == clean_value.lower()]
                    std_row[key] = matches[0] if matches else value.title()
            else:
                std_row[key] = value
                
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
        cat = row['Category']
        categories[cat] = categories.get(cat, 0) + 1
    
    print("\nCategory Distribution:")
    for cat, count in sorted(categories.items()):
        print(f"  {cat}: {count} products ({count/len(data)*100:.1f}%)")
    
    # Price analysis
    prices = [float(row['UnitPrice']) for row in data]
    print("\nPrice Statistics:")
    print(f"  Average Price: ${statistics.mean(prices):.2f}")
    print(f"  Median Price: ${statistics.median(prices):.2f}")
    print(f"  Price Range: ${min(prices):.2f} - ${max(prices):.2f}")
    
    # Branch distribution
    branches = {}
    for row in data:
        branch = row['Branch']
        branches[branch] = branches.get(branch, 0) + 1
    
    print("\nBranch Distribution:")
    for branch, count in sorted(branches.items()):
        print(f"  {branch}: {count} products ({count/len(data)*100:.1f}%)")
    
    print("=" * 50)

# Path to the raw products data file
input_file = "../../../Data/Raw/products_data.csv"
output_file = "../../../Data/Processed/products_data_cleaned.csv"

# Read and process the CSV file
with open(input_file, mode='r') as file:
    csv_reader = csv.DictReader(file)
    products_data = list(csv_reader)

print(f"Loaded {len(products_data)} product records.")

# Clean the data
print("Cleaning data...")
cleaned_data = handle_missing_values(products_data)
cleaned_data = remove_outliers(cleaned_data)
cleaned_data = standardize_format(cleaned_data)

# Generate summary
generate_summary(cleaned_data)

# Write the cleaned data to a new CSV file
with open(output_file, mode='w', newline='') as file:
    if cleaned_data:
        fieldnames = cleaned_data[0].keys()
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(cleaned_data)

print(f"\nCleaned data saved to: {output_file}")
