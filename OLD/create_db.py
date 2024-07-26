import sqlite3
import os
from constants import EXPORT_PATH, DB_FILE

def setup_database():
    if not os.path.exists(EXPORT_PATH):
        os.makedirs(EXPORT_PATH)

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS price_data (
            company_id TEXT,
            date TEXT,
            open REAL,
            high REAL,
            low REAL,
            close REAL,
            volume INTEGER,
            PRIMARY KEY (company_id, date)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS kpi_summary (
            company_id TEXT,
            year INTEGER,
            period INTEGER,
            kpi_id INTEGER,
            kpi_value REAL,
            PRIMARY KEY (company_id, year, period, kpi_id)
        )
    ''')

    conn.commit()
    conn.close()
    print(f"Database created at {DB_FILE}")

if __name__ == "__main__":
    setup_database()
