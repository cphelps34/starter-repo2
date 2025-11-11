-- Create sales fact table
CREATE TABLE IF NOT EXISTS sales (
    transaction_id TEXT PRIMARY KEY,
    sale_date TEXT,  -- ISO format: YYYY-MM-DD
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
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_sales_customer ON sales(customer_id);
CREATE INDEX IF NOT EXISTS idx_sales_product ON sales(product_id);
CREATE INDEX IF NOT EXISTS idx_sales_date ON sales(sale_date);
CREATE INDEX IF NOT EXISTS idx_sales_store ON sales(store_id);
