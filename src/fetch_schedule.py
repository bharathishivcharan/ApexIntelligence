import fastf1 
import os 
import pandas as pd

def get_2026_schedule():
     if not os.path.exists('cache'): 
        os.makedirs('cache') 
        fastf1.Cache.enable_cache('cache') 
        print("Fetching 2026 schedule!") 
        schedule = fastf1.get_event_schedule(2026) 
        clean_schedule = schedule[['RoundNumber', 'EventName', 'EventDate', 'Country']] 
        if not os.path.exists('data'): 
            os.makedirs('data') 
            clean_schedule.to_csv('data/f1_2026_calendar.csv', index=False) 
            print("Success!")

if __name__ == "main": 
    get_2026_schedule()