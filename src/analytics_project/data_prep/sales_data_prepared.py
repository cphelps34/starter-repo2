import csv
import statistics
from datetime import datetime
from typing import List, Dict

def handle_missing_values(data: List[Dict]) -> List[Dict]:
    """Handle missing values in the sales data."""
    cleaned_data = []
    for row in data:
        # Replace empty strings, ',' and '?' with None
        row = {k: (None if v in ['', ',', '?'] else v) for k, v in row.items()}
        
        # Skip rows with missing TransactionID (our primary key)
        if row.get('TransactionID') is None:
            continue
            
        # Set defaults for missing values
        defaults = {
            'CustomerID': '000000',
            'ProductID': '0000',
            'StoreID': '000',
            'CampaignID': '0',
            'SaleAmount': '0.00',
            'Expenses': '0.00',
            'Coast': 'Unknown'
        }
        
        for field, default in defaults.items():
            if field in row and (row[field] is None or row[field] == '?'):
                row[field] = default
            
        # Fill missing values with appropriate defaults
        defaults = {
            'PaymentMethod': 'Unknown',
            'Discount': '0.00',
            'Status': 'Completed'
        }
        
        for field, default in defaults.items():
            if field in row and (row[field] is None or row[field] == '?'):
                row[field] = default
                
        cleaned_data.append(row)
    return cleaned_data

def validate_relationships(data: List[Dict]) -> List[Dict]:
    """Validate customer and product IDs against their respective files."""
    valid_data = []
    initial_count = len(data)
    print(f"Initial record count before validation: {initial_count}")
    
    def standardize_customer_id(cid: str) -> str:
        """Standardize customer ID to 6-digit format."""
        try:
            return str(int(cid)).zfill(6)
        except (ValueError, TypeError):
            return cid
            
    def standardize_product_id(pid: str) -> str:
        """Standardize product ID to 4-digit format."""
        try:
            return str(int(pid)).zfill(4)
        except (ValueError, TypeError):
            return pid
    
    # Read customer IDs from cleaned customer data
    customer_ids = set()
    try:
        with open("../../../Data/Processed/customers_data_cleaned.csv", 'r') as f:
            customer_reader = csv.DictReader(f)
            customer_ids = {standardize_customer_id(row['CustomerID']) for row in customer_reader}
            print(f"Found {len(customer_ids)} valid customer IDs")
    except FileNotFoundError:
        print("Warning: Cleaned customers data not found. Skipping customer validation.")
        customer_ids = {standardize_customer_id(row['CustomerID']) for row in data}  # Use all customer IDs as valid
        print(f"Using {len(customer_ids)} customer IDs from sales data")
    
    # Read product IDs from cleaned product data
    product_ids = set()
    try:
        with open("../../../Data/Processed/products_data_cleaned.csv", 'r') as f:
            product_reader = csv.DictReader(f)
            product_ids = {standardize_product_id(row['ProductID']) for row in product_reader}
            print(f"Found {len(product_ids)} valid product IDs")
    except FileNotFoundError:
        print("Warning: Cleaned products data not found. Skipping product validation.")
        product_ids = {standardize_product_id(row['ProductID']) for row in data}  # Use all product IDs as valid
        print(f"Using {len(product_ids)} product IDs from sales data")
    
    # Print some sample IDs for debugging
    print("\nSample standardized customer IDs from reference data:", list(sorted(customer_ids))[:5])
    print("Sample standardized product IDs from reference data:", list(sorted(product_ids))[:5])
    
    # Validate relationships
    invalid_customers = set()
    invalid_products = set()
    for row in data:
        valid = True
        std_cust_id = standardize_customer_id(row['CustomerID'])
        std_prod_id = standardize_product_id(row['ProductID'])
        
        if std_cust_id not in customer_ids:
            invalid_customers.add(std_cust_id)
            valid = False
        if std_prod_id not in product_ids:
            invalid_products.add(std_prod_id)
            valid = False
        if valid:
            valid_data.append(row)
    
    if invalid_customers:
        print("\nInvalid Customer IDs found (standardized):")
        print(', '.join(sorted(invalid_customers)[:10]), '...' if len(invalid_customers) > 10 else '')
    
    if invalid_products:
        print("\nInvalid Product IDs found (standardized):")
        print(', '.join(sorted(invalid_products)[:10]), '...' if len(invalid_products) > 10 else '')
    
    print(f"\nValid records after validation: {len(valid_data)} ({len(valid_data)/initial_count*100:.1f}%)")        
    return valid_data

def remove_outliers(data: List[Dict]) -> List[Dict]:
    """Remove outliers from sales amount and expenses using IQR method."""
    cleaned_data = data.copy()
    
    for field in ['SaleAmount', 'Expenses']:
        values = [float(row[field]) for row in data]
        
        # Calculate Q1, Q3 and IQR
        q1 = statistics.quantiles(values, n=4)[0]
        q3 = statistics.quantiles(values, n=4)[2]
        iqr = q3 - q1
        
        # Define outlier bounds
        lower_bound = max(0, q1 - 1.5 * iqr)  # Don't allow negative values
        upper_bound = q3 + 1.5 * iqr
        
        # Filter out outliers
        cleaned_data = [row for row in cleaned_data 
                       if lower_bound <= float(row[field]) <= upper_bound]
    
    return cleaned_data

def standardize_format(data: List[Dict]) -> List[Dict]:
    """Standardize data formats."""
    standardized_data = []
    today = datetime.now().strftime('%Y-%m-%d')  # Default to today for invalid dates
    
    for row in data:
        std_row = {}
        
        for key, value in row.items():
            # Handle None and '?' values
            if value is None or value == '?':
                if key in ['SaleDate']:
                    std_row[key] = today  # Use today's date for missing dates
                elif key in ['SaleAmount', 'Expenses']:
                    std_row[key] = '0.00'  # Use 0.00 for missing amounts
                else:
                    std_row[key] = None
                continue
            
            if key == 'TransactionID':
                # Ensure 6-digit transaction ID
                try:
                    std_row[key] = str(int(value)).zfill(6)
                except ValueError:
                    std_row[key] = '000000'
            elif key == 'CustomerID':
                # Ensure 6-digit customer ID
                try:
                    std_row[key] = str(int(value)).zfill(6)
                except ValueError:
                    std_row[key] = '000000'
            elif key == 'ProductID':
                # Ensure 4-digit product ID
                try:
                    std_row[key] = str(int(value)).zfill(4)
                except ValueError:
                    std_row[key] = '0000'
            elif key == 'SaleDate':
                # Standardize date format to YYYY-MM-DD
                try:
                    date = datetime.strptime(str(value), '%m/%d/%Y')
                    std_row[key] = date.strftime('%Y-%m-%d')
                except ValueError:
                    try:
                        date = datetime.strptime(str(value), '%Y-%m-%d')
                        std_row[key] = value
                    except ValueError:
                        std_row[key] = today  # Use today's date for invalid dates
            elif key == 'SaleAmount':
                # Format to 2 decimal places
                try:
                    std_row[key] = f"{float(value):.2f}"
                except ValueError:
                    std_row[key] = '0.00'
            elif key == 'Expenses':
                # Format to 2 decimal places
                try:
                    std_row[key] = f"{float(value):.2f}"
                except ValueError:
                    std_row[key] = '0.00'
            elif key == 'Coast':
                # Standardize coast names
                std_row[key] = str(value).strip().title() or 'Unknown'
            elif key == 'StoreID':
                # Ensure 3-digit store ID
                try:
                    std_row[key] = str(int(value)).zfill(3)
                except ValueError:
                    std_row[key] = '000'
            elif key == 'CampaignID':
                # Ensure campaign ID is a single digit
                try:
                    std_row[key] = str(int(value))
                except ValueError:
                    std_row[key] = '0'
            else:
                std_row[key] = str(value).strip()
                
        standardized_data.append(std_row)
    
    return standardized_data

def remove_duplicates(data: List[Dict]) -> List[Dict]:
    """Remove duplicate sales records based on TransactionID."""
    seen_ids = set()
    unique_data = []
    
    for row in data:
        if row['TransactionID'] not in seen_ids:
            seen_ids.add(row['TransactionID'])
            unique_data.append(row)
            
    return unique_data

def generate_summary(data: List[Dict]) -> None:
    """Generate and print a summary of the cleaned sales data."""
    print("\nSales Data Cleaning Summary:")
    print("=" * 50)
    
    # Record counts
    print(f"Total sales records processed: {len(data)}")
    
    # Date range
    dates = [datetime.strptime(row['SaleDate'], '%Y-%m-%d') for row in data]
    print("\nDate Range:")
    print(f"  Earliest Sale: {min(dates).strftime('%Y-%m-%d')}")
    print(f"  Latest Sale: {max(dates).strftime('%Y-%m-%d')}")
    
    # Coast distribution
    coasts = {}
    for row in data:
        coast = row['Coast']
        coasts[coast] = coasts.get(coast, 0) + 1
    
    print("\nCoast Distribution:")
    for coast, count in sorted(coasts.items()):
        print(f"  {coast}: {count} sales ({count/len(data)*100:.1f}%)")
    
    # Store distribution
    stores = {}
    for row in data:
        store = row['StoreID']
        stores[store] = stores.get(store, 0) + 1
    
    print("\nStore Distribution:")
    for store, count in sorted(stores.items()):
        print(f"  Store {store}: {count} sales ({count/len(data)*100:.1f}%)")
    
    # Campaign distribution
    campaigns = {}
    for row in data:
        campaign = row['CampaignID']
        campaigns[campaign] = campaigns.get(campaign, 0) + 1
    
    print("\nCampaign Distribution:")
    for campaign, count in sorted(campaigns.items()):
        print(f"  Campaign {campaign}: {count} sales ({count/len(data)*100:.1f}%)")
    
    # Sales statistics
    amounts = [float(row['SaleAmount']) for row in data]
    print("\nSales Amount Statistics:")
    print(f"  Average Amount: ${statistics.mean(amounts):.2f}")
    print(f"  Median Amount: ${statistics.median(amounts):.2f}")
    print(f"  Total Sales: ${sum(amounts):.2f}")
    print(f"  Min Amount: ${min(amounts):.2f}")
    print(f"  Max Amount: ${max(amounts):.2f}")
    
    # Expenses statistics
    expenses = [float(row['Expenses']) for row in data]
    print("\nExpenses Statistics:")
    print(f"  Average Expenses: ${statistics.mean(expenses):.2f}")
    print(f"  Median Expenses: ${statistics.median(expenses):.2f}")
    print(f"  Total Expenses: ${sum(expenses):.2f}")
    print(f"  Min Expenses: ${min(expenses):.2f}")
    print(f"  Max Expenses: ${max(expenses):.2f}")
    
    print("=" * 50)

# Path to the raw sales data file
input_file = "../../../Data/Raw/sales_data.csv"
output_file = "../../../Data/Processed/sales_data_cleaned.csv"

# Read and process the CSV file
with open(input_file, mode='r') as file:
    csv_reader = csv.DictReader(file)
    sales_data = list(csv_reader)

print(f"Loaded {len(sales_data)} sales records.")

# Clean the data
print("Cleaning data...")
cleaned_data = handle_missing_values(sales_data)
cleaned_data = validate_relationships(cleaned_data)
cleaned_data = remove_outliers(cleaned_data)
cleaned_data = standardize_format(cleaned_data)
cleaned_data = remove_duplicates(cleaned_data)

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
