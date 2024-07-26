import sqlite3

def check_columns():
    conn = sqlite3.connect('Exportdata/borsdata_monthly.db')
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(factor_rankings)")
    columns = cursor.fetchall()
    for column in columns:
        print(column)
    conn.close()

if __name__ == "__main__":
    check_columns()
