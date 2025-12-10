import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), 'db.sqlite3')
print(f"Database: {db_path}")
print("=" * 80)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get table schema
print("\n### LEADS TABLE SCHEMA ###\n")
cursor.execute("PRAGMA table_info(leads);")
columns = cursor.fetchall()
for col in columns:
    print(f"{col[0]:2}. {col[1]:30} {col[2]:15} {'NOT NULL' if col[3] else 'NULL':10}")

# Get all lead data
print("\n### LEAD DATA ###\n")
cursor.execute("SELECT * FROM leads;")
column_names = [desc[0] for desc in cursor.description]
rows = cursor.fetchall()

print(f"Total leads: {len(rows)}\n")

if rows:
    for row in rows:
        print("=" * 80)
        for i, value in enumerate(row):
            # Truncate long values
            if value and isinstance(value, str) and len(value) > 60:
                display_value = value[:60] + "..."
            else:
                display_value = value
            print(f"{column_names[i]:25}: {display_value}")
        print()
else:
    print("No leads found in database")

conn.close()
print("=" * 80)
