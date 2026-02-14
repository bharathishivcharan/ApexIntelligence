import sqlite3

def clean_database():
    conn = sqlite3.connect('data/f1_data.db')
    cursor = conn.cursor()

    # 1. SEE WHAT WE HAVE
    print("Current Tables:")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    print(cursor.fetchall())

    # 2. DELETE (DROP) THE DUPLICATES/MESSY ONES
    # Replace 'table_to_delete' with the actual messy names you see in the list above
    # Example: cursor.execute("DROP TABLE IF EXISTS telemetry_LEC_old")
   # cursor.execute("DROP TABLE IF EXISTS telemetry_LECMonaco2025") 
    
    # 3. RENAME FOR POLISH
    # Convention: Driver_Event_Year (e.g., LEC_Monaco_2025)
    # Syntax: ALTER TABLE old_name RENAME TO new_name
    
    try:
        # Example: Renaming the long messy name to something clean
        # cursor.execute("ALTER TABLE telemetry_LEC_Monaco_2025 RENAME TO LEC_Monaco_2025")
        # cursor.execute("ALTER TABLE telemetry_HAM_Monaco_2025 RENAME TO HAM_Monaco_2025")
        print("\nRenaming successful (if tables existed).")
    except Exception as e:
        print(f"\nNote: {e}")

    conn.commit()
    conn.close()
    print("\nDatabase is clean!")

if __name__ == "__main__":
    clean_database()