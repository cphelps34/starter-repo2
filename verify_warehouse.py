"""Quick verification script for the data warehouse."""
import sqlite3

conn = sqlite3.connect('dw/smart_sales.sqlite')
cur = conn.cursor()

# List all tables
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cur.fetchall()
print("Tables created:")
for t in tables:
    print(f"  - {t[0]}")

print()

# Count rows in each table
cur.execute("SELECT COUNT(*) FROM customers")
print(f"Customers: {cur.fetchone()[0]} rows")

cur.execute("SELECT COUNT(*) FROM products")
print(f"Products: {cur.fetchone()[0]} rows")

cur.execute("SELECT COUNT(*) FROM sales")
print(f"Sales: {cur.fetchone()[0]} rows")

print("\n--- Sample Query: Top 5 Products by Revenue ---")
cur.execute("""
    SELECT p.product_name, p.category, SUM(s.sale_amount) as revenue
    FROM sales s
    JOIN products p ON s.product_id = p.product_id
    GROUP BY p.product_id, p.product_name, p.category
    ORDER BY revenue DESC
    LIMIT 5
""")
results = cur.fetchall()
for row in results:
    print(f"  {row[0]:30s} | {row[1]:15s} | ${row[2]:,.2f}")

print("\n--- Sample Query: Sales by Region ---")
cur.execute("""
    SELECT c.region, COUNT(*) as num_sales, SUM(s.sale_amount) as total_revenue
    FROM sales s
    JOIN customers c ON s.customer_id = c.customer_id
    GROUP BY c.region
    ORDER BY total_revenue DESC
""")
results = cur.fetchall()
for row in results:
    print(f"  {row[0]:15s} | {row[1]:4d} sales | ${row[2]:,.2f}")

conn.close()
print("\n✓ Data warehouse verified successfully!")
