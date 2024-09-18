import subprocess
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import time
from anomaly_detection.config import Config
from anomaly_detection.database import DatabaseHandler
import os
import sys

# Configuration
DB_HANDLER = DatabaseHandler(
    Config.DB_NAME,
    Config.DB_USER,
    Config.DB_PASSWORD,
    Config.DB_HOST,
    Config.DB_PORT,
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

UPDATE_INTERVAL = 2  # seconds
TABLE_NAME = Config.TABLE_NAME
WINDOW_LIMIT = 3000

if "execute_flag" not in st.session_state:
    st.session_state.execute_flag = False


def execute_scripts():
    """Execute the data generation and prediction scripts."""
    if not st.session_state.execute_flag:
        st.session_state.execute_flag = True
        subprocess.Popen(
            [
                sys.executable,
                os.path.join(BASE_DIR, "anomaly_detection", "predictor.py"),
            ]
        )
        time.sleep(3)
        subprocess.Popen(
            [
                sys.executable,
                os.path.join(BASE_DIR, "anomaly_detection", "data_generator.py"),
            ]
        )

        time.sleep(7)


def get_data() -> pd.DataFrame:
    data = DB_HANDLER.fetch_new_data(TABLE_NAME, limit=WINDOW_LIMIT)

    if data is not None:
        data = pd.DataFrame(data)
        # Convert 'isanomaly' to boolean and ensure 'date' is datetime
        data["isanomaly"] = data["isanomaly"].astype(str).str.lower() == "true"
        data["date"] = pd.to_datetime(data["date"])

        return data
    else:
        return None


if __name__ == "__main__":
    st.set_page_config(
        page_title="Anomaly Detection",
        page_icon="✅",
        layout="wide",
    )

    with st.sidebar:
        st.header("Configuration")
        if st.button("Start Execution"):
            execute_scripts()  # Start the execution scripts

    # Placeholder for the chart (initially empty)
    chart_placeholder = st.empty()

    # Create the figure and axes once, outside the loop
    fig, ax = plt.subplots(figsize=(16, 8))

    while st.session_state.execute_flag:
        data = get_data()
        if data is not None:
            # Clear the previous plot
            ax.clear()

            # Plot the new data
            ax.plot(data["date"], data["high"], label="Highest Price")
            ax.scatter(
                data[data["isanomaly"]]["date"],
                data[data["isanomaly"]]["high"],
                color="red",
                label="Anomalies",
            )
            ax.set_xlabel("Date")
            ax.set_ylabel("Price")
            ax.set_title("Highest Price Trend with Anomaly Detection")
            ax.legend()

            chart_placeholder.pyplot(fig)  # Display the plot

        time.sleep(UPDATE_INTERVAL)
