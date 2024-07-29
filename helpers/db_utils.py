import sqlite3
from borsdata_api.constants import DB_FILE_MONTHLY

def connect_db():
    """
    Connects to the SQLite database and returns the connection object.
    """
    print("Connecting to the database...")
    return sqlite3.connect(DB_FILE_MONTHLY)

def backup_and_remove_existing_db(db_file):
    """
    Backs up the existing database and removes the original file.
    """
    import os
    import shutil
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
