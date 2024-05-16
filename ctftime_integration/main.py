import os
from package import get_future_events, clean_events, save_2_xl, find_new_ctfs

# Variables
days = 100 # Day limit: the code will browse for CTFs from today until the given limit 
restriction_list = ['Open', 'Individual', 'High-school'] # Filter the CTF you're interested in depending on the restriction types
useless_columns = ['ctf_id','weight', 'logo', 'live_feed', 'format', 'participants', 'public_votable', 'is_votable_now', 'prizes', 'organizers', 'format_id', 'duration', 'onsite', 'location', 'ctftime_url', 'restrictions'] # Columns you don't need for your integration
artifact_location = "\\artifacts\\events.xlsx"

# Get current working directory
cwd = os.getcwd()
# Concatenate the final file path
file_path = cwd+artifact_location

events = get_future_events(day_limit=days)
print(f"Retrieved {len(events)} CTFs for the next {days} days")

events_df = clean_events(events=events, restriction_list=restriction_list, useless_columns=useless_columns)    
print(f"After data cleaning we found {events_df.shape[0]} interesting CTFs for you.")

new_events = find_new_ctfs(events_df=events_df, file_path=file_path)
if new_events.shape[0] == 0:
    print("You have already found all the interesting CTFs for the given time period.")
else:
    print(f"Found {new_events.shape[0]} new CTFs for you.")

save_2_xl(events_df=events_df, file_path=file_path)
print(f"Future events stored in CSV file {file_path}")