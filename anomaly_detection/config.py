import os


class Config:
    # Database configuration
    DB_NAME = "your_database_name"
    DB_USER = "your_database_user"
    DB_PASSWORD = "your_database_password"
    DB_HOST = "your_database_host"
    DB_PORT = "your_database_port"

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    # Anomaly detection configuration
    SEQUENCE_LENGTH = 24 * 4
    SCALER_PATH = os.path.join(BASE_DIR, "..", "utils", "scaler2.pkl")
    DESCALER_PATH = os.path.join(BASE_DIR, "..", "utils", "descaler.pkl")
    DATA_GENERATION_PATH = os.path.join(BASE_DIR, "..", "data", "BTC_Hourly_2021.csv")
    TABLE_NAME = "btcdata"
    MODEL_PATH = os.path.join(BASE_DIR, "..", "utils", "BTC_Model.pth")
    TARGET_COLUMN = "high"
    DATE_COLUMN = "date"
    DEVICE_TYPE = "cpu"
    THRESHOLD = 0.5

    # Data generation configuration
    FREQUENCY = 1.0  # Data generation frequency in seconds
