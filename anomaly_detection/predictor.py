import torch
import numpy as np
import pandas as pd
import pickle
from flask import Flask, request, jsonify
from database import DatabaseHandler
from anomaly_detection.config import Config
from anomaly_detection.models import BTCPredictor, BTCPrdictionModel, BTCDataset, BTCDataModule


class AnomalyPredictorService:
    def __init__(self):
        self.device = Config.DEVICE_TYPE
        self.model = torch.load(Config.MODEL_PATH, map_location=torch.device(self.device))
        self.model.eval()
        self.scaler = pickle.load(open(Config.SCALER_PATH, "rb"))
        self.descaler = pickle.load(open(Config.DESCALER_PATH, "rb"))
        self.db_handler = DatabaseHandler(
            Config.DB_NAME,
            Config.DB_USER,
            Config.DB_PASSWORD,
            Config.DB_HOST,
            Config.DB_PORT,
        )
        self.app = Flask(__name__)

        # Attach the predict method to the Flask app
        self.app.route("/predict_anomaly", methods=["POST"])(self.predict)

    def prepare_data_for_model(self, latest_data):
        """
        Prepares the latest data from the database for model input.
        """
        latest_df = pd.DataFrame(latest_data)
        latest_df[Config.DATE_COLUMN] = pd.to_datetime(
            latest_df[Config.DATE_COLUMN], utc=True
        )
        latest_df.set_index(Config.DATE_COLUMN, inplace=True)
        latest_df.sort_index(inplace=True)
        latest_df.drop(["isanomaly"], axis=1, inplace=True)

        # Convert all columns to numeric
        for col in latest_df.columns:
            if latest_df[col].dtype == "object":
                try:
                    latest_df[col] = pd.to_numeric(latest_df[col])
                except ValueError:
                    print(f"Warning: Could not convert column '{col}' to numeric")

        sequence = torch.Tensor(latest_df.to_numpy()).unsqueeze(0).to(self.device)
        return sequence

    def model_predict(self, X):
        """
        Predicts using the model.
        """
        with torch.no_grad():
            _, output = self.model(X)
            prediction = output.squeeze().cpu().numpy()
        return float(prediction)

    def is_anomaly(self, real_value, predicted_value):
        """
        Determines if it's an anomaly.
        """
        mae = abs(real_value - predicted_value)
        print(predicted_value, real_value, mae)
        return mae > Config.THRESHOLD

    def predict(self):
        """
        API endpoint to receive new data, process it, and return predictions.
        """
        try:
            new_data = request.get_json()

            latest_data = self.db_handler.fetch_new_data(
                Config.TABLE_NAME, limit=Config.SEQUENCE_LENGTH
            )

            X = self.prepare_data_for_model(latest_data)

            prediction_scaled = self.model_predict(X)

            label_value = float(new_data[Config.TARGET_COLUMN])
            label_scaled = self.descaler.transform(np.array([[label_value]]))

            anomaly_result = self.is_anomaly(label_scaled, prediction_scaled)

            new_data["isanomaly"] = bool(anomaly_result)

            self.db_handler.insert_data(Config.TABLE_NAME, new_data)

            return jsonify({"message": "Data was predicted succesfully"})

        except Exception as e:
            print(e)
            return jsonify({"error": str(e)}), 500

    def start(self):
        """
        Starts the Flask app.
        """
        self.app.run(debug=True)


if __name__ == "__main__":
    service = AnomalyPredictorService()
    service.start()
