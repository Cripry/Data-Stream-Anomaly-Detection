"""
This script generates data from a CSV file and stores it in a PostgreSQL database.

It preprocesses the DataFrame, creates a table with the same structure as the DataFrame (including an 'isAnomaly' column),
and populates the table with the data.

Usage:
   python generate_data.py

Requires:
   pandas
   time
   database_handler.py (a custom module for database interactions)
"""

import numpy as np
import pandas as pd
import time
from database import DatabaseHandler


def preprocess_df(df):
    """
    Preprocesses the DataFrame by setting 'Date and Hour' as the index,
    sorting by datetime in ascending order, and removing rows where
    the "Source" column contains "Wind."

    Args:
        df: The input DataFrame.

    Returns:
        The preprocessed DataFrame.
    """
    df["Date and Hour"] = pd.to_datetime(df["Date and Hour"], utc=True)

    # Remove rows where "Source" contains "Wind"
    df = df[df["Source"].str.contains("Wind") == False]

    df.set_index("Date and Hour", inplace=True)
    df.sort_index(inplace=True)
    return df


def create_table(df, db_handler, table_name):
    """
    Checks if the table exists. If not, creates the table with the same structure
    as the DataFrame.

    Args:
        df (pd.DataFrame): The DataFrame containing the data.
        db_handler (DatabaseHandler): An instance of the DatabaseHandler class.
        table_name (str): The name of the table to create.
    """

    columns = []
    for col in df.columns:
        if df[col].dtype == np.float64:
            data_type = "FLOAT"
        elif df[col].dtype == np.int64:
            data_type = "INTEGER"
        else:
            data_type = "VARCHAR(255)"
        columns.append(f"{col} {data_type}")

    columns.append("isAnomaly VARCHAR(255)")  # Add 'isAnomaly' column
    # Check if table exists
    exists = db_handler.cursor.execute(
        f"SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = '{table_name}');"
    )

    if not exists:
        db_handler.create_table(table_name, columns)


def data_generator(df, db_handler, table_name, frequency=1.0, start_index=30):
    """
    Continuously extracts elements from a DataFrame (all columns)
    and saves them to the specified database table in real-time.

    Args:
        df (pd.DataFrame): The DataFrame containing the data to be streamed.
        db_handler (DatabaseHandler): An instance of the DatabaseHandler class.
        table_name (str): The name of the table to insert data into.
        frequency (float, optional): The time interval (in seconds) between sending data points.
                                       Defaults to 1.0 (save every second).
        start_index (int, optional): The index from which to start iterating in the DataFrame.
                                       Defaults to 0.
    """

    preprocessed_df = preprocess_df(df.copy())

    exists = db_handler.cursor.execute(
        f"SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = '{table_name}');"
    )

    if not exists:
        create_table(preprocessed_df, db_handler, table_name)

    for index, row in enumerate(preprocessed_df.iterrows(), start=start_index):
        _, series_data = row
        data = series_data.to_dict()
        data["isAnomaly"] = None
        db_handler.insert_data(table_name, data)

        time.sleep(frequency)

    db_handler.close_connection()


if __name__ == "__main__":
    df = pd.read_csv(r"data\intermittent-renewables-production-france.csv")
    table_name = "SolarEnergyData"
    db_handler = DatabaseHandler()

    data_generator(df, db_handler, table_name)
