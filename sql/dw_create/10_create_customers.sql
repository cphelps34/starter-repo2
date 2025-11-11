-- Create customers dimension table
CREATE TABLE IF NOT EXISTS customers (
    customer_id TEXT PRIMARY KEY,
    age INTEGER,
    gender TEXT,
    location TEXT,
    membership_level TEXT,
    region TEXT,
    division TEXT,
    join_date TEXT  -- ISO format: YYYY-MM-DD
);
