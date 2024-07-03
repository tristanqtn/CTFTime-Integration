from ctf import get_ctf_delta, get_top_10_teams, get_team_object


def handle_response(message) -> str:
    """
    Handle the user message and return the appropriate response.

    Args:
        message (str): The message sent by the user.

    Returns:
        response (str): The response to the user message.
    """

    p_message = message.lower()

    if "!hello" in p_message:
        return "Hello! How can I help you today?\nType `!help` for a list of commands."

    elif "!newctf" in p_message:
        # Variables
        days = 100  # Day limit: the code will browse for CTFs from today until the given limit
        restriction_list = [
            "Open",
            "Individual",
            "High-school",
        ]  # Filter the CTF you're interested in depending on the restriction types
        useless_columns = [
            "ctf_id",
            "weight",
            "logo",
            "live_feed",
            "format",
            "participants",
            "public_votable",
            "is_votable_now",
            "prizes",
            "organizers",
            "format_id",
            "duration",
            "onsite",
            "location",
            "ctftime_url",
            "restrictions",
        ]  # Columns you don't need for your integration
        artifact_location = "\\artifacts\\events.xlsx"
        return get_ctf_delta(
            artifact_location, days, restriction_list, useless_columns
        ).to_string()

    elif "!newctf_name" in p_message:
        # Variables
        days = 100  # Day limit: the code will browse for CTFs from today until the given limit
        restriction_list = [
            "Open",
            "Individual",
            "High-school",
        ]  # Filter the CTF you're interested in depending on the restriction types
        useless_columns = [
            "ctf_id",
            "weight",
            "logo",
            "live_feed",
            "format",
            "participants",
            "public_votable",
            "is_votable_now",
            "prizes",
            "organizers",
            "format_id",
            "duration",
            "onsite",
            "location",
            "ctftime_url",
            "restrictions",
        ]  # Columns you don't need for your integration
        artifact_location = "\\artifacts\\events.xlsx"
        df = get_ctf_delta(artifact_location, days, restriction_list, useless_columns)
        return df["name"].to_string()

    elif "!top10" in p_message:
        return get_top_10_teams().to_string()

    elif "!team" in p_message:
        return get_team_object().display()

    # add parametrized year for ranking

    elif "!ranking" in p_message:
        return get_team_object().get_team_rank_given_year()

    elif "!help" in p_message:
        return "Commands:\n`!newctf`: Gives you all the upcoming CTF you weren't awared of.\n`!newctf_name`: Gives you the name of the upcoming CTF you weren't awared of.\n`!help`: Shows you this list of commands available."

    elif "!goodbye" in p_message:
        return "Goodbye! Have a great day!"
