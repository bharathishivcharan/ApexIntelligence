import sqlite3
import pandas as pd

def create_f1_database(): # Creating a database
    conn = sqlite3.connect('data/f1_data.db')
    print("Database created successfully.")

    #Connecting the csv file
    df = pd.read_csv('data/f1_2026_calendar.csv')

    #Saving it in the database
    df.to_sql('calendar', conn, if_exists='replace', index=False)
    
   #Close the connection
    conn.close()
    print("2026 Schedule has been moved into the SQL Database!")

if __name__ == "__main__":
    create_f1_database()