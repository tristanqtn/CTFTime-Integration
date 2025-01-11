import http.client
import datetime
import json
import pandas as pd

########################################################################################
# CTF Events
########################################################################################


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
    finish_timestamp = int(
        (now + datetime.timedelta(days=day_limit))
        .replace(tzinfo=datetime.timezone.utc)
        .timestamp()
    )

    # Set the API endpoint and parameters
    url = "/api/v1/events/"
    params = {"limit": 500, "start": start_timestamp, "finish": finish_timestamp}

    # Build the query string
    query_string = "?" + "&".join([f"{key}={value}" for key, value in params.items()])

    # Create an HTTPS connection to the CTFtime API
    conn = http.client.HTTPSConnection("ctftime.org")

    # Send a GET request to the API endpoint
    conn.request("GET", url + query_string)

    # Get the response from the API
    response = conn.getresponse()

    # Read the response body
    data = response.read().decode("utf-8")

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
    events_df["organizer_name"] = events_df["organizers"].apply(lambda x: x[0]["name"])

    # Computing the total duration of the event in hours and store it in a new column
    events_df["duration_hours"] = events_df["duration"].apply(
        lambda x: x["hours"] + x["days"] * 24
    )

    # Removing all onsite events
    events_df = events_df[events_df["onsite"] == False]

    # Keep only ctf where restrictions are in $restriction_list
    events_df = events_df[
        events_df["restrictions"].apply(lambda x: x in restriction_list)
    ]

    for restriction in restriction_list:
        # Add a boolean column named like the restriction that takes 1 if the value in restrictions is equal to the restriction
        events_df[restriction.lower()] = events_df["restrictions"].apply(
            lambda x: x == restriction
        )

    # Drop useless columns
    events_df = events_df.drop(useless_columns, axis=1)

    # Rename column id into ctftime_id
    events_df = events_df.rename(columns={"id": "ctftime_id"})

    return events_df


########################################################################################
# Top Teams
########################################################################################


def get_top_teams():
    """
    Get the information of the top teams.

    Returns:
        - A JSON string containing the information of the top teams.
    """

    # Set the API endpoint and parameters
    url = "/api/v1/top/"
    params = {"limit": 10}

    # Build the query string
    query_string = "?" + "&".join([f"{key}={value}" for key, value in params.items()])

    # Create an HTTPS connection to the CTFtime API
    conn = http.client.HTTPSConnection("ctftime.org")

    # Send a GET request to the API endpoint
    conn.request("GET", url + query_string)

    # Get the response from the API
    response = conn.getresponse()

    # Read the response body
    data = response.read().decode("utf-8")

    # Parse the JSON data
    return json.loads(data)


def parse_top_teams(top_teams, year):
    """
    Parse the JSON string containing the information of the top teams into a list of Team objects.

    Parameters:
        - `top_teams`: A JSON string containing the information of the top teams.

    Returns:
        - A dataframe containing the top teams.
    """
    # Creates a dictionary from the JSON string
    content = top_teams.get(str(year), None)

    # Transform to df and return it
    return pd.DataFrame(content)


def get_top_10_teams(year):
    """
    Get the top 10 teams.

    Returns:
        - A dataframe containing the top 10 teams.
    """

    top_teams = get_top_teams()
    return parse_top_teams(top_teams, year)


########################################################################################
# Team
########################################################################################


class Team:
    """
    A class to represent a CTF Time team.

    Attributes:
        - `team_id`: The ID of the team.
        - `primary_alias`: The primary alias of the team.
        - `name`: The name of the team.
        - `country`: The country of the team.
        - `rating`: The rating of the team trough the years.
        - `logo`: The logo of the team.
        - `academic` : A boolean indicating if the team is an academic team.
        - `aliases` : A list of aliases of the team.

    Methods:
        - `display()`: Display the name of the team.
        - `get_team_rank_given_year(year)`: Get the rank of the team for a given year.
    """

    def __init__(
        self, team_id, primary_alias, name, rating, country, logo, aliases, academic
    ):
        self.team_id = team_id
        self.primary_alias = primary_alias
        self.name = name
        self.rating = rating
        self.country = country
        self.logo = logo
        self.aliases = aliases
        self.academic = academic

    def display(self):
        print(f"Team {self.name} with id {self.team_id} and rating {self.rating}")

    def get_team_rank_given_year(self, year=datetime.datetime.now().year):
        year = str(year)
        year_ratings = self.rating.get(year, None)
        return year_ratings


def get_team_info(team_id):
    """
    Get the information of a team given its ID.

    Parameters:
        - `team_id`: The ID of the team.

    Returns:
        - A JSON string containing the information of the team.
    """

    # Set the API endpoint and parameters
    url = "/api/v1/teams/" + team_id + "/"

    # Create an HTTPS connection to the CTFtime API
    conn = http.client.HTTPSConnection("ctftime.org")

    # Send a GET request to the API endpoint
    conn.request("GET", url)

    # Get the response from the API
    response = conn.getresponse()

    # Read the response body
    data = response.read().decode("utf-8")

    return data


def parse_team_info(team):
    """
    Parse the JSON string containing the information of a team into a Team object.

    Parameters:
        - `team`: A JSON string containing the information of the team.

    Returns:
        - A Team object.
    """

    # Creates a dictionary from the JSON string
    team_dict = json.loads(team)

    # Create a Team object
    team = Team(
        team_id=team_dict["id"],
        primary_alias=team_dict["primary_alias"],
        name=team_dict["name"],
        rating=team_dict["rating"],
        country=team_dict["country"],
        logo=team_dict["logo"],
        aliases=team_dict["aliases"],
        academic=team_dict["academic"],
    )
    return team


def get_team_object(team_id="216659"):
    """
    Get the Team object given the ID of the team. by default it will use the id defined in the variables.

    Parameters:
        - `team_id`: The ID of the team.

    Returns:
        - A Team object.
    """
    team = get_team_info(team_id)
    return parse_team_info(team)
