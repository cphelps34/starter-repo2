"""
scripts/dw_create/create_dw_sqlite.py

This script creates the SQLite data warehouse using .sql files.

File locations:
- data/prepared         : cleaned and prepared CSVs (used later in ETL)
- dw/                   : data warehouse folder
- dw/smart_sales.sqlite : SQLite database file
- sql/dw_create         : folder for .sql files used to create tables

Notes:
- SQLite does not support a native DATE type.
  Dates should be stored as TEXT in ISO format: "YYYY-MM-DD".
"""

# import from Python standard libraries
import pathlib
import sys
import sqlite3

# import from external libraries
import pandas as pd

# Add project root to sys.path for local imports
sys.path.append(str(pathlib.Path(__file__).resolve().parent.parent.parent))

# import from local modules
from utils.logger import logger

# === Path Constants ===

# Python script directories
SCRIPTS_DW_CREATE_DIR = pathlib.Path(__file__).resolve().parent
SCRIPTS_DIR = SCRIPTS_DW_CREATE_DIR.parent

# Project root directory
PROJECT_ROOT = SCRIPTS_DIR.parent

# Data directories
DATA_DIR = PROJECT_ROOT / "data"
DATA_PREPARED_DIR = DATA_DIR / "prepared"

# SQL directories
SQL_DIR = PROJECT_ROOT / "sql"
SQL_DW_CREATE_DIR = SQL_DIR / "dw_create"

# Output DW directory
DW_DIR = PROJECT_ROOT / "dw"

# Output DW SQLite database path
DW_PATH = DW_DIR / "smart_sales.sqlite"

# Ensure necessary directories exist
DW_DIR.mkdir(parents=True, exist_ok=True)
SQL_DW_CREATE_DIR.mkdir(parents=True, exist_ok=True)

# === Functions ===

def run_sql_file(conn, file_path: pathlib.Path) -> None:
    """Run a SQL script file using the given connection."""
    logger.info(f"RUN: {file_path}")
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            sql = f.read()
            conn.executescript(sql)
    except Exception as e:
        logger.error(f"Error running {file_path.name}: {e}")
        raise


def create_dw() -> None:
    """Create the data warehouse schema using SQLite."""
    logger.info("Creating data warehouse using SQLite...")

    # Check if required SQL files exist
    sql_files = list(SQL_DW_CREATE_DIR.glob("*.sql"))
    if not sql_files:
        logger.error(f"No .sql files in {SQL_DW_CREATE_DIR}. Please add schema files before running.")
        exit(22)

    conn = None
    try:
        conn = sqlite3.connect(DW_PATH)

        # Run SQL scripts for creating tables
        # Use version 90 for sales table
        run_sql_file(conn, SQL_DW_CREATE_DIR / "00_drop_all_tables.sql")
        run_sql_file(conn, SQL_DW_CREATE_DIR / "10_create_customers.sql")
        run_sql_file(conn, SQL_DW_CREATE_DIR / "20_create_products.sql")
        run_sql_file(conn, SQL_DW_CREATE_DIR / "90_create_sales.sql")

        logger.info("Data warehouse schema created successfully.")

    except sqlite3.Error as e:
        logger.error(f"SQLite error: {e}")
        exit(23)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        exit(24)
    finally:
        if conn:
            conn.close()


def populate_dw() -> None:
    """Populate the SQLite data warehouse with cleaned data."""
    logger.info("Populating SQLite data warehouse from prepared CSVs...")

    try:
        conn = sqlite3.connect(DW_PATH)

        # --- Load and insert customers ---
        df_customers = pd.read_csv(DATA_PREPARED_DIR / "customers_data_cleaned.csv")
        df_customers = df_customers.rename(columns={
            "CustomerID": "customer_id",
            "Age": "age",
            "Gender": "gender",
            "Location": "location",
            "MembershipLevel": "membership_level",
            "Region": "region",
            "Division": "division",
            "JoinDate": "join_date"
        })
        # Only keep columns that exist in the dataframe
        customer_cols = [
            "customer_id", "age", "gender", "location", "membership_level",
            "region", "division", "join_date"
        ]
        df_customers = df_customers[[col for col in customer_cols if col in df_customers.columns]]
        # Drop duplicate customer IDs, keeping first occurrence
        df_customers = df_customers.drop_duplicates(subset=['customer_id'], keep='first')
        df_customers.to_sql("customers", conn, if_exists="append", index=False)
        logger.info(f"Inserted {len(df_customers)} rows into customers table.")

        # --- Load and insert products ---
        df_products = pd.read_csv(DATA_PREPARED_DIR / "products_data_cleaned.csv")
        df_products = df_products.rename(columns={
            "ProductID": "product_id",
            "ProductName": "product_name",
            "Category": "category",
            "UnitPrice": "unit_price",
            "Model": "model",
            "Branch": "branch"
        })
        product_cols = [
            "product_id", "product_name", "category", "unit_price", "model", "branch"
        ]
        df_products = df_products[[col for col in product_cols if col in df_products.columns]]
        # Drop duplicate product IDs, keeping first occurrence
        df_products = df_products.drop_duplicates(subset=['product_id'], keep='first')
        df_products.to_sql("products", conn, if_exists="append", index=False)
        logger.info(f"Inserted {len(df_products)} rows into products table.")

        # --- Load and insert sales ---
        df_sales = pd.read_csv(DATA_PREPARED_DIR / "sales_data_cleaned.csv")
        df_sales = df_sales.rename(columns={
            "TransactionID": "transaction_id",
            "SaleDate": "sale_date",
            "CustomerID": "customer_id",
            "ProductID": "product_id",
            "StoreID": "store_id",
            "CampaignID": "campaign_id",
            "SaleAmount": "sale_amount",
            "Expenses": "expenses",
            "Coast": "coast",
            "PaymentMethod": "payment_method",
            "Discount": "discount",
            "Status": "status"
        })
        # Keep all relevant sales columns for analytics
        sales_cols = [
            "transaction_id", "sale_date", "customer_id", "product_id",
            "store_id", "campaign_id", "sale_amount", "expenses",
            "coast", "payment_method", "discount", "status"
        ]
        df_sales = df_sales[[col for col in sales_cols if col in df_sales.columns]]
        # Drop duplicate transaction IDs, keeping first occurrence
        df_sales = df_sales.drop_duplicates(subset=['transaction_id'], keep='first')
        df_sales.to_sql("sales", conn, if_exists="append", index=False)
        logger.info(f"Inserted {len(df_sales)} rows into sales table.")

        logger.info("All tables populated successfully.")

    except Exception as e:
        logger.error(f"Error populating SQLite data warehouse: {e}")
        exit(1)
    finally:
        if conn:
            conn.close()


def main() -> None:
    """Main function to run the warehouse creation process."""
    logger.info("========================================")
    logger.info("Starting: create_dw_sqlite.py")
    logger.info("========================================")
    logger.info(f"Root:   {PROJECT_ROOT}")
    logger.info(f"Scripts:{SCRIPTS_DW_CREATE_DIR}")
    logger.info(f"SQL:    {SQL_DW_CREATE_DIR}")
    logger.info(f"Input:  {DATA_PREPARED_DIR}")
    logger.info(f"Output: {DW_PATH}")
    create_dw()
    populate_dw()
    logger.info("========================================")
    logger.info("Finished: create_dw_sqlite.py")
    logger.info("========================================")


if __name__ == "__main__":
    main()
