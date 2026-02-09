import fastf1
import pandas as pd

def get_2026_schedule():
    print("Fetching the 2026 F1 Season Schedule...")
    
    # Getting the 2026 calendar
    schedule = fastf1.get_event_schedule(2026)
    
    # Columns = (Race Name, Country, Date)
    clean_schedule = schedule[['RoundNumber', 'EventName', 'EventDate', 'Country']]
    
    # Saving it as CSV
    clean_schedule.to_csv('data/f1_2026_calendar.csv', index=False)
    
    print(" Schedule saved to data/f1_2026_calendar.csv")
    print(clean_schedule.head()) # Checking the first few races in terminal

if __name__ == "__main__":
    get_2026_schedule()