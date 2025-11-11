# Data Warehouse Creation Script

## Overview
This script creates a SQLite data warehouse from your cleaned CSV files and populates it with data.

## Prerequisites
1. Cleaned CSV files must exist in `data/prepared/`:
   - `customers_data_cleaned.csv`
   - `products_data_cleaned.csv`
   - `sales_data_cleaned.csv`

2. Required Python packages:
   - pandas
   - sqlite3 (built-in)

## Usage

Run from the project root:

```powershell
cd C:\Repos\starter-repo2
python scripts/dw_create/create_dw_sqlite.py
```

## Output
- SQLite database: `dw/smart_sales.sqlite`
- Tables created:
  - `customers` - Customer dimension
  - `products` - Product dimension
  - `sales` - Sales fact table with foreign keys

## Schema

### Customers Table
- customer_id (TEXT, PRIMARY KEY)
- age (INTEGER)
- gender (TEXT)
- location (TEXT)
- membership_level (TEXT)
- region (TEXT)
- division (TEXT)
- join_date (TEXT, ISO format)

### Products Table
- product_id (TEXT, PRIMARY KEY)
- product_name (TEXT)
- category (TEXT)
- unit_price (REAL)
- model (TEXT)
- branch (TEXT)

### Sales Table
- transaction_id (TEXT, PRIMARY KEY)
- sale_date (TEXT, ISO format)
- customer_id (TEXT, FOREIGN KEY)
- product_id (TEXT, FOREIGN KEY)
- store_id (TEXT)
- campaign_id (TEXT)
- sale_amount (REAL)
- expenses (REAL)
- coast (TEXT)
- payment_method (TEXT)
- discount (REAL)
- status (TEXT)

Indexes are created on customer_id, product_id, sale_date, and store_id for optimal query performance.

## Example Queries

Connect to the database and run analytics queries:

```python
import sqlite3
conn = sqlite3.connect('dw/smart_sales.sqlite')

# Total sales by region
query = """
SELECT c.region, SUM(s.sale_amount) as total_sales
FROM sales s
JOIN customers c ON s.customer_id = c.customer_id
GROUP BY c.region
ORDER BY total_sales DESC
"""
```

Or use the SQLite command line:

```powershell
sqlite3 dw/smart_sales.sqlite
```

```sql
-- Top products by revenue
SELECT p.product_name, p.category, SUM(s.sale_amount) as revenue
FROM sales s
JOIN products p ON s.product_id = p.product_id
GROUP BY p.product_id, p.product_name, p.category
ORDER BY revenue DESC
LIMIT 10;
```
