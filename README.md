# starter-repo2

Data analytics project with ETL pipeline and SQLite data warehouse.

## Features

- **Data Preparation Pipeline**: Modular ETL scripts for cleaning and standardizing customer, product, and sales data
- **Shared Utilities**: Common data scrubbing functions for ID standardization, date parsing, outlier removal, and duplicate handling
- **SQLite Data Warehouse**: Star schema with dimension (customers, products) and fact (sales) tables
- **Quality Controls**: Referential integrity validation, missing value handling, outlier detection
- **Testing**: Unit tests for data scrubber utilities and prep modules
- **Documentation**: MkDocs site with Material theme

## Project Structure

```
starter-repo2/
├── Data/
│   ├── Processed/          # Cleaned CSV outputs
│   │   ├── customers_data_cleaned.csv
│   │   ├── products_data_cleaned.csv
│   │   └── sales_data_cleaned.csv
│   └── Raw/                # Source data
│       ├── customers_data.csv
│       ├── products_data.csv
│       └── sales_data.csv
├── dw/
│   └── smart_sales.sqlite  # Data warehouse
├── sql/
│   └── dw_create/          # DDL scripts
├── scripts/
│   ├── data_preparation/   # Legacy scripts
│   └── dw_create/          # DW creation script
├── src/
│   └── analytics_project/
│       └── data_prep/      # ETL modules
│           ├── data_scrubber.py         # Shared utilities
│           ├── customer_data_prepared.py
│           ├── product_data_prepared.py
│           ├── sales_data_prepared.py
│           └── create_data_warehouse.py
├── tests/                  # Unit tests
├── docs/                   # MkDocs documentation
└── mkdocs.yml
```

## Quick Start

### Prerequisites

- Python 3.8+
- uv (recommended) or pip

### Installation

1. Clone the repository:
```powershell
git clone https://github.com/cphelps34/starter-repo2.git
cd starter-repo2
```

2. Install dependencies (using uv):
```powershell
uv sync
```

Or with traditional pip:
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .
```

### Running the Data Pipeline

Execute the full ETL pipeline:

```powershell
# 1. Clean customer data
uv run python -m analytics_project.data_prep.customer_data_prepared

# 2. Clean product data
uv run python -m analytics_project.data_prep.product_data_prepared

# 3. Clean sales data (validates against customers & products)
uv run python -m analytics_project.data_prep.sales_data_prepared

# 4. Load data warehouse
uv run --with pandas python scripts/dw_create/create_dw_sqlite.py
```

### Running Tests

```powershell
# Run all tests
uvx pytest

# Run with coverage
uvx pytest --cov=src/analytics_project
```

### Building Documentation

```powershell
# Build docs
uvx --from mkdocs-material mkdocs build --strict

# Serve docs locally
uvx --from mkdocs-material mkdocs serve
```

## Data Preparation Modules

### Shared Utilities (`data_scrubber.py`)

Common functions used across all prep modules:

- **`standardize_id()`**: Zero-pad IDs to fixed width with optional prefix
- **`standardize_numeric()`**: Parse and format numeric values with validation
- **`standardize_date()`**: Flexible date parsing supporting multiple formats
- **`clean_string()`**: Normalize text with proper spacing and capitalization
- **`handle_missing_values()`**: Fill missing values with specified defaults
- **`remove_outliers()`**: IQR or z-score based outlier detection
- **`remove_duplicates()`**: Deduplicate based on key field(s)

### Customer Data Preparation

**Input**: `Data/Raw/customers_data.csv`  
**Output**: `Data/Processed/customers_data_cleaned.csv`  
**Records**: 199 (from 203 raw)

Key transformations:
- Standardize CustomerID to 6-digit format (e.g., `001000`)
- Parse and normalize join dates to YYYY-MM-DD
- Remove age outliers using IQR method
- Standardize region and division names
- Fill missing values with defaults (Gender: Unknown, MembershipLevel: Basic)

### Product Data Preparation

**Input**: `Data/Raw/products_data.csv`  
**Output**: `Data/Processed/products_data_cleaned.csv`  
**Records**: 100

Key transformations:
- Standardize ProductID to 4-digit format (e.g., `2000`)
- Normalize category names (Electronics, Clothing, Home, Office)
- Clean product names and branch locations
- Remove price outliers
- Ensure numeric unit prices with 2 decimal places

### Sales Data Preparation

**Input**: `Data/Raw/sales_data.csv`  
**Output**: `Data/Processed/sales_data_cleaned.csv`  
**Records**: 1,913 (from 2,001 raw)

Key transformations:
- Validate referential integrity against cleaned customer/product data
- Standardize TransactionID, CustomerID, ProductID formats
- Parse sale dates to YYYY-MM-DD
- Remove outliers from SaleAmount and Expenses
- Handle missing payment methods, discounts, status
- Remove duplicate transactions

Invalid records removed:
- 3 invalid customer IDs (001164, 001193, 009999)
- 21 records failed validation (99.0% retention)
- 67 duplicates removed

## Data Warehouse

### Schema

**Dimension Tables:**
- `customers` (198 rows): customer_id (PK), age, gender, location, membership_level, region, division, join_date
- `products` (100 rows): product_id (PK), product_name, category, unit_price, model, branch

**Fact Table:**
- `sales` (1,913 rows): transaction_id (PK), sale_date, customer_id (FK), product_id (FK), store_id, campaign_id, sale_amount, expenses, coast, payment_method, discount, status

**Indexes:**
- idx_sales_customer, idx_sales_product, idx_sales_date, idx_sales_store

### Querying the Warehouse

```python
import sqlite3

conn = sqlite3.connect('dw/smart_sales.sqlite')

# Top products by revenue
query = """
SELECT p.product_name, p.category, 
       SUM(s.sale_amount) as total_revenue
FROM sales s
JOIN products p ON s.product_id = p.product_id
GROUP BY p.product_id
ORDER BY total_revenue DESC
LIMIT 10
"""

results = conn.execute(query).fetchall()
```
## Development

### Code Quality

The project uses pre-commit hooks for code quality:

```powershell
# Install pre-commit hooks
uvx pre-commit install

# Run manually
uvx pre-commit run --all-files
```

Configured hooks:
- **black**: Code formatting
- **isort**: Import sorting
- **flake8**: Linting and style checks
- **trailing-whitespace**: Cleanup
- **end-of-file-fixer**: Ensure newlines

### Project Standards

- **ID Formats**: CustomerID (6 digits), ProductID (4 digits), TransactionID (6 digits)
- **Date Format**: YYYY-MM-DD (ISO 8601)
- **Numeric Precision**: Currency values to 2 decimal places
- **Missing Values**: Handled with sensible defaults, never left as NULL in cleaned data
- **Outliers**: Removed using IQR method (threshold=1.5) for numeric fields

## Repository Information

- **GitHub**: https://github.com/cphelps34/starter-repo2
- **Branch**: master
- **License**: MIT (if applicable)

## Recent Updates (November 2025)

- Refactored data prep modules to use shared `data_scrubber` utilities
- Fixed `standardize_numeric()` signature (use `decimals` param)
- Added proper entry points for all prep modules
- Created SQLite data warehouse with star schema
- Updated pre-commit hooks to latest versions
- Comprehensive test coverage for data scrubber functions
- MkDocs documentation with Material theme

## Next Steps

Potential improvements:
- Add more dimension tables (Date, Store, Campaign)
- Implement incremental ETL for updates
- Add data quality reporting dashboard
- Create dbt models for transformations
- Add CI/CD pipeline for automated testing

````
