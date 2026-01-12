import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'dictionary.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print("Tables in database:")
for table in tables:
    print(f"  - {table[0]}")

# Get schema for each table
for table in tables:
    table_name = table[0]
    print(f"\nSchema for '{table_name}':")
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    for col in columns:
        print(f"  {col[1]} ({col[2]})")
    
    # Show sample data
    cursor.execute(f"SELECT * FROM {table_name} LIMIT 5")
    rows = cursor.fetchall()
    print(f"\nSample data from '{table_name}':")
    for row in rows:
        print(f"  {row}")
    
    # Get count
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    count = cursor.fetchone()[0]
    print(f"\nTotal rows in '{table_name}': {count:,}")

conn.close()
