import numpy as np
import pandas as pd
import time
import requests
from anomaly_detection.database import DatabaseHandler
from anomaly_detection.config import Config


class DataGeneratorService:
    def __init__(self, df_path):
        self.db_handler = DatabaseHandler(
            Config.DB_NAME,
            Config.DB_USER,
            Config.DB_PASSWORD,
            Config.DB_HOST,
            Config.DB_PORT,
        )
        self.df = pd.read_csv(df_path)

    def preprocess_df(self):
        """Preprocesses the DataFrame."""
        self.df["date"] = pd.to_datetime(self.df["date"], utc=True)
        self.df.columns = [column.replace(" ", "") for column in self.df.columns]
        self.df.sort_values(by="date", inplace=True)

    def create_and_prepopulate_table(self):
        """Creates and prepopulates the table if it doesn't exist."""
        columns = []
        for col in self.df.columns:
            if self.df[col].dtype == np.float64:
                data_type = "FLOAT"
            elif self.df[col].dtype == np.int64:
                data_type = "INTEGER"
            elif self.df[col].dtype == "datetime64[ns, UTC]":
                data_type = "TIMESTAMP"
            else:
                data_type = "VARCHAR(255)"
            columns.append(f"{col} {data_type}")

        columns.append("isAnomaly VARCHAR(255)")

        try:
            self.db_handler.cursor.execute(
                f"SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = '{Config.TABLE_NAME}');"
            )
            exists = self.db_handler.cursor.fetchone()[0]

            if not exists:
                self.db_handler.create_table(Config.TABLE_NAME, columns)

                # Prepopulate the table
                for _, row in self.df.iloc[: Config.SEQUENCE_LENGTH].iterrows():
                    data = row.to_dict()
                    data["isAnomaly"] = False
                    if "date" in data and isinstance(data["date"], pd.Timestamp):
                        data["date"] = data["date"].isoformat()
                    self.db_handler.insert_data(Config.TABLE_NAME, data)

        except Exception as e:
            print(f"Error creating or prepopulating table: {e}")

    def start(self):
        """Starts the data generation process."""
        self.preprocess_df()
        self.create_and_prepopulate_table()

        for _, row in enumerate(self.df.iloc[Config.SEQUENCE_LENGTH:].iterrows()):
            _, series_data = row
            data = series_data.to_dict()

            if "date" in data and isinstance(data["date"], pd.Timestamp):
                data["date"] = data["date"].isoformat()

            try:
                response = requests.post(
                    "http://127.0.0.1:5000/predict_anomaly", json=data
                )
                response.raise_for_status()
                print(f"Data sent successfully. Response: {response.text}")
            except requests.exceptions.RequestException as e:
                print(f"Error sending data: {e}")

            time.sleep(Config.FREQUENCY)

        self.db_handler.close_connection()


if __name__ == "__main__":
    data_file_path = Config.DATA_GENERATION_PATH
    service = DataGeneratorService(data_file_path)
    service.start()
