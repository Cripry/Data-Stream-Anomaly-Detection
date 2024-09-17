import numpy as np
import pandas as pd
import time
from database import DatabaseHandler


def preprocess_df(df):
    """
    Preprocesses the DataFrame by setting 'Time' as the index,
    sorting by datetime in ascending order

    Args:
        df: The input DataFrame.

    Returns:
        The preprocessed DataFrame.
    """
    df["date"] = pd.to_datetime(df["date"], utc=True)
    df.drop(columns=["unix", "symbol", "Volume USD"], axis=1, inplace=True)
    df.columns = [column.replace(" ", "") for column in df.columns]
    df.sort_values(by="date", inplace=True)
    return df


def create_table(df, db_handler, table_name):
    """
    Checks if the table exists. If not, creates the table with the same structure
    as the DataFrame, including an 'isAnomaly' column

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

    columns.append("isAnomaly VARCHAR(255)")

    try:
        db_handler.cursor.execute(
            f"SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = '{table_name}');"
        )
        exists = db_handler.cursor.fetchone()[0]

        if not exists:
            db_handler.create_table(table_name, columns)
    except Exception as e:
        print(f"Error creating table: {e}")


def data_generator(df, db_handler, table_name, frequency=1.0, start_index=0):
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

    # Create table if it doesn't exist
    create_table(preprocessed_df, db_handler, table_name)

    for index, row in enumerate(preprocessed_df.iterrows(), start=start_index):
        _, series_data = row
        data = series_data.to_dict()
        data["isAnomaly"] = None  # Initialize 'isAnomaly'
        db_handler.insert_data(table_name, data)
        time.sleep(frequency)

    db_handler.close_connection()


if __name__ == "__main__":
    df = pd.read_csv(r"data\BTC-Hourly.csv")
    table_name = "BTCData"
    db_handler = DatabaseHandler()
    data_generator(df, db_handler, table_name)
