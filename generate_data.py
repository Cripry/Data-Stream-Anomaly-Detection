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
    Continuously extracts elements from a DataFrame (all columns)
    and sends them to a specified endpoint in real-time, with a configurable sending frequency.

    Args:
        df (pd.DataFrame): The DataFrame containing the data to be streamed.
        endpoint (str): The URL of the endpoint where data elements are sent.
        frequency (float, optional): The time interval (in seconds) between sending data points.
                                       Defaults to 1.0 (send every second).

    Raises:
        ValueError: If the DataFrame is empty.
    """

    if df.empty:
        raise ValueError("The DataFrame must contain data.")

    while True:
        for _, row in df.iterrows():
            data = row.to_dict()  # Convert row to dictionary
            requests.post(endpoint, json=data)  # Send as JSON
            time.sleep(frequency)


if __name__ == "__main__":
    df = pd.read_csv(r"data\intermittent-renewables-production-france.csv")
    endpoint = os.getenv("ENDPOINT_DATA_COLLECTION")

    data_generator(df, endpoint)
