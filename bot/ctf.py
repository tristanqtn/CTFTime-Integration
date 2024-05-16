import http.client
import datetime
import json
import pandas as pd
import os

def get_future_events(day_limit):
    """
    Retrieves a list of future CTF events from the CTFtime API within the specified number of days.

    Args:
        day_limit (int): The number of days in the future to retrieve events for.

    Returns:
        A list of dictionaries containing the event data.
    """
    # Get the current date and time
    now = datetime.datetime.now(datetime.UTC)

    # Calculate the start and finish timestamps
    start_timestamp = int(now.timestamp())
    finish_timestamp = int((now + datetime.timedelta(days=day_limit)).replace(tzinfo=datetime.timezone.utc).timestamp())

    # Set the API endpoint and parameters
    url = '/api/v1/events/'
    params = {
        'limit': 500,
        'start': start_timestamp,
        'finish': finish_timestamp
    }

    # Build the query string
    query_string = '?' + '&'.join([f'{key}={value}' for key, value in params.items()])

    # Create an HTTPS connection to the CTFtime API
    conn = http.client.HTTPSConnection('ctftime.org')

    # Send a GET request to the API endpoint
    conn.request('GET', url + query_string)

    # Get the response from the API
    response = conn.getresponse()

    # Read the response body
    data = response.read().decode('utf-8')

    # Parse the JSON data
    return json.loads(data)

def clean_events(events, restriction_list, useless_columns):
    """
    Cleans and processes the event data retrieved from the CTFtime API.

    Args:
        events (pandas.DataFrame): The DataFrame containing the event data.
        restriction_list (list): The list of allowed restrictions for the events.
        useless_columns (list): The list of columns to drop from the DataFrame.

    Returns:
        A cleaned and processed DataFrame containing the event data.
    """
    events_df = pd.DataFrame(events)

    # Extract organizer named from organizer dictionary
    events_df['organizer_name'] = events_df['organizers'].apply(lambda x: x[0]['name'])

    # Computing the total duration of the event in hours and store it in a new column
    events_df['duration_hours'] = events_df['duration'].apply(lambda x: x['hours'] + x['days']*24)

    # Removing all onsite events
    events_df = events_df[events_df['onsite'] == False]

    # Keep only ctf where restrictions are in $restriction_list
    events_df = events_df[events_df['restrictions'].apply(lambda x: x in restriction_list)]

    for restriction in restriction_list:
        # Add a boolean column named like the restriction that takes 1 if the value in restrictions is equal to the restriction
        events_df[restriction.lower()] = events_df['restrictions'].apply(lambda x: x == restriction)

    # Drop useless columns
    events_df = events_df.drop(useless_columns, axis=1)

    # Rename column id into ctftime_id
    events_df = events_df.rename(columns={'id': 'ctftime_id'})

    return events_df


def find_new_ctfs(events_df, file_path):
    """
    Loads previously found CTFs from Excel file and compares with recently retrieved CTFs.

    Args:
        events_df (pandas.DataFrame): The cleaned and processed DataFrame containing the fresh event data.
        file_path (str): The file path to load the Excel file.
        
    Returns:
        new_events (pandas.DataFrame): A DataFrame containing the new CTFs that were not present in the Excel file.
    """
    existing_events = pd.read_excel(file_path)
    # Find the unregistered events
    new_events = events_df[~events_df['ctftime_id'].isin(existing_events['ctftime_id'])]
    return new_events

def save_2_xl(events_df, file_path):
    """
    Saves the cleaned and processed event data to an Excel file.

    Args:
        events_df (pandas.DataFrame): The cleaned and processed DataFrame containing the event data.
        file_path (str): The file path to save the Excel file to.
    """
    # Save DataFrame to Excel file
    events_df.to_excel(file_path, index=False)
    
def get_ctf_delta(artifact_location, days, restriction_list, useless_columns):
    """
    Retrieves the new upcoming CTF events not present in the Excel file and add them to the Excel.
    
    Args:
        artifact_location (str): The partial location of the Excel file (relative to the main).
        days (int): The number of days in the future to retrieve events for.
        restriction_list (list): The list of allowed restrictions for the events.
        useless_columns (list): The list of columns to drop from the DataFrame.
    
    Returns:
        A DF containing the new CTF events that were not present in the Excel file.
    """
    
    # Get current working directory
    cwd = os.getcwd()
    # Concatenate the final file path
    file_path = cwd+artifact_location

    events = get_future_events(day_limit=days)
    events_df = clean_events(events=events, restriction_list=restriction_list, useless_columns=useless_columns)    
    new_events = find_new_ctfs(events_df=events_df, file_path=file_path)
    save_2_xl(events_df=events_df, file_path=file_path)

    if new_events.shape[0] == 0:
        return "You have already found all the interesting CTFs for the given time period."
    else:
        return new_events
