import sqlite3
import os
import shutil
from borsdata_api.constants import DB_FILE_MONTHLY

def backup_and_remove_existing_db(db_file):
    if os.path.exists(db_file):
        version = 1
        backup_file = f"{db_file}_v{version}"
        while os.path.exists(backup_file):
            version += 1
            backup_file = f"{db_file}_v{version}"
        shutil.copy2(db_file, backup_file)
        print(f"Existing database backed up as {backup_file}")
        os.remove(db_file)
        print(f"Existing database {db_file} removed.")

def create_tables():
    conn = sqlite3.connect(DB_FILE_MONTHLY)
    cursor = conn.cursor()

    # Create table for monthly price data
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS monthly_price_data (
            ins_id INTEGER,
            date TEXT,
            open REAL,
            high REAL,
            low REAL,
            close REAL,
            volume INTEGER,
            PRIMARY KEY (ins_id, date)
        )
    ''')
    print("Table 'monthly_price_data' created or already exists.")

    # Create table for monthly report data
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS monthly_report_data (
            ins_id INTEGER,
            year INTEGER,
            period INTEGER,
            revenues REAL,
            gross_income REAL,
            operating_income REAL,
            profit_before_tax REAL,
            profit_to_equity_holders REAL,
            earnings_per_share REAL,
            number_of_shares REAL,
            dividend REAL,
            intangible_assets REAL,
            tangible_assets REAL,
            financial_assets REAL,
            non_current_assets REAL,
            cash_and_equivalents REAL,
            current_assets REAL,
            total_assets REAL,
            total_equity REAL,
            non_current_liabilities REAL,
            current_liabilities REAL,
            total_liabilities_and_equity REAL,
            net_debt REAL,
            cash_flow_from_operating_activities REAL,
            cash_flow_from_investing_activities REAL,
            cash_flow_from_financing_activities REAL,
            cash_flow_for_the_year REAL,
            free_cash_flow REAL,
            stock_price_average REAL,
            stock_price_high REAL,
            stock_price_low REAL,
            report_start_date TEXT,
            report_end_date TEXT,
            broken_fiscal_year BOOLEAN,
            currency TEXT,
            currency_ratio REAL,
            net_sales REAL,
            report_date TEXT,
            PRIMARY KEY (ins_id, report_start_date, report_end_date)
        )
    ''')
    print("Table 'monthly_report_data' created or already exists.")

    conn.commit()
    conn.close()
    print("Tables created successfully in the monthly database.")

if __name__ == "__main__":
    backup_and_remove_existing_db(DB_FILE_MONTHLY)
    create_tables()
    print("Database setup complete.")
