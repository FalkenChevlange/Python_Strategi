import sqlite3
import pandas as pd

# Koppla till databasen
conn = sqlite3.connect('borsdata_monthly.db')
cursor = conn.cursor()

# Hämta en lista över tabeller i databasen
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print("Tables in the database:", tables)

# Visa kolumnerna i varje tabell för att verifiera deras struktur
for table in tables:
    print(f"\nColumns in table {table[0]}:")
    cursor.execute(f"PRAGMA table_info({table[0]});")
    columns = cursor.fetchall()
    for column in columns:
        print(column)

conn.close()
