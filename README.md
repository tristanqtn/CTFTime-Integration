# CTFtime API Event Retrieval and Cleaning

## Overview

This program retrieves a list of future CTF events from the CTFtime API, cleans and processes the data, and saves it to an Excel file. The program is written in Python and uses the http.client, json, pandas, and os libraries.

## Proof of Concept

A proof of concept (POC) has been developed in a Jupyter [Notebook](./poc.ipynb) to demonstrate the functionality of the CTFtime event retrieval and cleaning solution. We recommend that users study this notebook carefully to understand how the solution works.

For the dependencies required to run the notebook, we recommend that users manually install them in a virtual environment (venv) to avoid any conflicts with other Python projects. The required dependencies are as follows:

- http.client
- json
- pandas
- os
- openpyxl

To install these dependencies, you can follow these steps:

1. Create a virtual environment using the python `-m venv venv` command.
2. Activate the virtual environment using the `source venv/bin/activate` command (on Windows, use `venv\Scripts\activate`).
3. Install the required dependencies using the `pip install http.client json pandas os` command.

Once you have installed the dependencies, you can run the Jupyter Notebook and use the solution as described in the notebook. If you have any questions or issues, please let us know.

## Program Workflow

The program consists of three main functions:

- `get_future_events(day_limit)`: Retrieves a list of future CTF events from the CTFtime API within the specified number of days.
- `clean_events(events_df, restriction_list, useless_columns)`: Cleans and processes the event data retrieved from the CTFtime API.
- `save_2_xl(events_df, artifact_location)`: Saves the cleaned and processed event data to an Excel file.

### `get_future_events(day_limit)`

This function takes a single argument day_limit, which specifies the number of days in the future to retrieve events for. The function sends a GET request to the CTFtime API with the appropriate parameters and retrieves the JSON response. The response is then parsed and returned as a list of dictionaries containing the event data.

### `clean_events(events_df, restriction_list, useless_columns)`

This function takes three arguments:

- `events_df`: The DataFrame containing the event data.
- `restriction_list`: The list of allowed restrictions for the events.
- `useless_columns`: The list of columns to drop from the DataFrame.

The function first extracts the organizer name from the organizer dictionary and stores it in a new column. It then computes the total duration of the event in hours and stores it in a new column. The function removes all onsite events and keeps only those events where the restrictions are in the specified restriction_list. It then adds a boolean column for each restriction in the restriction_list, indicating whether the event has that restriction. The function drops the useless columns specified in useless_columns and renames the id column to ctftime_id. The cleaned and processed DataFrame is then returned.

### `save_2_xl(events_df, artifact_location)`

This function takes two arguments:

- `events_df`: The cleaned and processed DataFrame containing the event data.
- `artifact_location`: The file path of the Excel file to save the data to.

The function saves the DataFrame to the specified Excel file using the to_excel() method.

## Usage

To use this program, follow these steps:

1. Clone the repo:

```shell
git clone https://github.com/tristanqtn/CTFTime-Integration.git
cd CTFTime-Integration
```

2. Install required dependencies using Poetry (Poetry will automatically create the venv to run the solution):

```shell
poetry install
```

3. Set the variables for a custom execution:

   - day_limit variable to the number of days in the future to retrieve events for.
   - restriction_list variable to the list of allowed restrictions for the events.
   - useless_columns variable to the list of columns to drop from the DataFrame.
   - artifact_location variable to the file path of the Excel file to save the data to.

4. Run the program using poetry:

```shell
poetry run .\ctftime_integration\main.py
```

The program will retrieve the event data from the CTFtime API, clean and process the data, and save it to the specified Excel file.

## Conclusion

This program provides a simple and efficient way to retrieve, clean, and process CTF event data from the CTFtime API. The program can be easily customized to suit specific requirements by modifying the day_limit, restriction_list, useless_columns, and artifact_location variables.

## Authors

**tristanqtn** : tristan.querton@gmail.com

This project is supported by members of the cybersecurity association and CTF team **0xECE**.
