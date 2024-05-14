from package import get_future_events, clean_events, save_2_xl

# Variables
days = 30 # Day limit: the code will browse for CTFs from today until the given limit 
restriction_list = ['Open', 'Individual', 'High-school'] # Filter the CTF you're interested in depending on the restriction types
useless_columns = ['ctf_id','weight', 'logo', 'live_feed', 'format', 'participants', 'public_votable', 'is_votable_now', 'prizes', 'organizers', 'format_id', 'duration', 'onsite', 'location', 'ctftime_url', 'restrictions'] # Columns you don't need for your integration
artifact_location = "\\artifacts\\events.xlsx"

events = get_future_events(day_limit=days)
print(f"Retrieved {len(events)} CTFs for the next {days} days")

events_df = clean_events(events=events, restriction_list=restriction_list, useless_columns=useless_columns)    
print(f"After data cleaning we found {events_df.shape[0]} interesting CTFs for you.")

file_path = save_2_xl(events_df=events_df, artifact_location=artifact_location)
print(f"Future events stored in CSV file {file_path}")