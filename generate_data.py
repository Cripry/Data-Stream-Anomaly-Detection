"""
This script streams data from a CSV file to a specified endpoint.

It loads the CSV data into a DataFrame, extracts the 'Power' column,
and sends each element to the endpoint in real-time.

"""

import pandas as pd
import time
import requests
import os
from dotenv import load_dotenv

load_dotenv()


def data_generator(df: pd.DataFrame, endpoint: str, frequency: float = 1.0) -> None:
    """
    Continuously extracts elements from a DataFrame ('Power' column)
    and sends them to a specified endpoint in real-time, with a configurable sending frequency.

    Args:
        df (pd.DataFrame): The DataFrame containing the data to be streamed.
        endpoint (str): The URL of the endpoint where data elements are sent.
        frequency (float, optional): The time interval (in seconds) between sending data points.
                                       Defaults is 1 (every second).

    Raises:
        ValueError: If the 'Power' column is not found in the DataFrame.
        ValueError: If the frequency is less than or equal to zero.
    """

    if "Power" not in df.columns:
        raise ValueError("The DataFrame must contain a column named 'Power'")

    if frequency <= 0:
        raise ValueError("Frequency must be a positive number greater than zero.")

    while True:
        for index, row in df.iterrows():
            element = row["Power"]
            requests.post(endpoint, data={"element": element})
            time.sleep(frequency)


if __name__ == "__main__":
    df = pd.read_csv(r"data\Location1.csv")
    endpoint = os.getenv("ENDPOINT_DATA_COLLECTION")

    data_generator(df, endpoint)
