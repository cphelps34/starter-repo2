"""
Script to create a SQLite data warehouse and load cleaned data from CSVs.
"""
import sqlite3
import csv
import os

# Paths to cleaned CSVs
CUSTOMERS_CSV = os.path.join('..', '..', '..', 'Data', 'Processed', 'customers_data_cleaned.csv')
PRODUCTS_CSV = os.path.join('..', '..', '..', 'Data', 'Processed', 'products_data_cleaned.csv')
SALES_CSV = os.path.join('..', '..', '..', 'Data', 'Processed', 'sales_data_cleaned.csv')

# Path to SQLite database
DB_PATH = os.path.join('..', '..', '..', 'Data', 'Warehouse', 'analytics_warehouse.db')
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

def create_tables(conn):
    cur = conn.cursor()
    # Customers dimension
    cur.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            customer_id TEXT PRIMARY KEY,
            age INTEGER,
            gender TEXT,
            location TEXT,
            membership_level TEXT,
            region TEXT,
            division TEXT,
            join_date TEXT
        )
    ''')
    # Products dimension
    cur.execute('''
        CREATE TABLE IF NOT EXISTS products (
            product_id TEXT PRIMARY KEY,
            product_name TEXT,
            category TEXT,
            unit_price REAL,
            model TEXT,
            branch TEXT
        )
    ''')
    # Sales fact table
    cur.execute('''
        CREATE TABLE IF NOT EXISTS sales (
            transaction_id TEXT PRIMARY KEY,
            sale_date TEXT,
            customer_id TEXT,
            product_id TEXT,
            store_id TEXT,
            campaign_id TEXT,
            sale_amount REAL,
            expenses REAL,
            coast TEXT,
            payment_method TEXT,
            discount REAL,
            status TEXT,
            FOREIGN KEY(customer_id) REFERENCES customers(customer_id),
            FOREIGN KEY(product_id) REFERENCES products(product_id)
        )
    ''')
    conn.commit()

def load_csv_to_table(conn, csv_path, table, columns):
    with open(csv_path, 'r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = [tuple(row.get(col, None) for col in columns) for row in reader]
    placeholders = ','.join(['?'] * len(columns))
    conn.executemany(f'INSERT OR IGNORE INTO {table} ({','.join(columns)}) VALUES ({placeholders})', rows)
    conn.commit()

def main():
    conn = sqlite3.connect(DB_PATH)
    create_tables(conn)
    # Load customers
    customer_cols = ['CustomerID','Age','Gender','Location','MembershipLevel','Region','Division','JoinDate']
    load_csv_to_table(conn, CUSTOMERS_CSV, 'customers', [c.lower() for c in customer_cols])
    # Load products
    product_cols = ['ProductID','ProductName','Category','UnitPrice','Model','Branch']
    load_csv_to_table(conn, PRODUCTS_CSV, 'products', [c.lower() for c in product_cols])
    # Load sales
    sales_cols = ['TransactionID','SaleDate','CustomerID','ProductID','StoreID','CampaignID','SaleAmount','Expenses','Coast','PaymentMethod','Discount','Status']
    load_csv_to_table(conn, SALES_CSV, 'sales', [c.lower() for c in sales_cols])
    print('Data warehouse created and loaded successfully.')
    conn.close()

if __name__ == '__main__':
    main()
