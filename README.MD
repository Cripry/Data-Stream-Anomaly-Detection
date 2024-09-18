
# Bitcoin Anomaly Detective 🕵️‍♂️

**Uncover Unusual Activity in Bitcoin Transactions**

This project focuses on identifying anomalies in Bitcoin transactions using a forecasting-based approach. A powerful LSTM model learns transactional patterns to predict the next highest price for transactions within the next hour. Any significant deviation (measured by Mean Absolute Error - MAE) from the predicted price is flagged as a potential anomaly.


The `data_generator.py` module serves as the engine driving the real-time simulation. It dynamically generates a database table if one doesn't already exist, and populates it with historical Bitcoin transaction data from 2021.

The core objective is to forecast the peak Bitcoin value within each hour and subsequently identify any market anomalies. To mimic a continuous data stream, the generator transmits data to the `/predict_anomaly` endpoint (established by the `Predictor` module) at a frequency specified in the `config.py` file.


## Features 🚀

* **Real-time Anomaly Detection:** Simulates real-time data streaming to detect anomalies as they occur.
* **LSTM-Based Forecasting:**  Employs a Long Short-Term Memory (LSTM) neural network to capture complex patterns in Bitcoin price data.
* **Data-Driven Insights:** Leverages historical Bitcoin transaction data for model training and anomaly identification.
* **Streamlit Visualization:** Provides an interactive Streamlit application to display the price chart with highlighted anomalies.

## Tech Stack 💻

* **Machine Learning:** PyTorch Lightning
* **Web Framework:** Flask
* **Data Visualization:** Streamlit
* **Database:** PostgreSQL

## Getting Started 🛠️

**Prerequisites:**

* **PostgreSQL 16:** Install PostgreSQL 16 from the official website: https://www.postgresql.org/
* **Python 3.12.2:** Ensure you have Python 3.12.2 installed.

**Installation and Setup:**

1. **Clone the repository:**

   `git clone  https://github.com/Cripry/Data-Stream-Anomaly-Detection.git`
2. **Create a virtual environment (recommended):**

   ```
   python -m venv anomaly_env
   source anomaly_env/bin/activate  # On Windows, use anomaly_env\Scripts\activate
   ```
3. **Install dependencies:**

   ```
   pip install -r requirements.txt
   ```
4. **Configure Database:**

   * Create a PostgreSQL database, user, and password.
   * Update the `config.py` file with your **database credentials:

     ```
     DB_NAME = "your_database_name"
     DB_USER = "your_database_user"
     DB_PASSWORD = "your_database_password"
     DB_HOST = "your_database_host"
     DB_PORT = "your_database_port"**
     ```
5. **Run the Streamlit app:**

   `streamlit run app.py`

## Project Structure 📂

* `anomaly_detection`: Core project code for data handling, model, and prediction
* `data`: Contains the Bitcoin transaction dataset (`BTC_Hourly_2021.csv`)
* `Jupyter Notebooks`: Jupyter notebook used for model training and development
* `utils`: Stores model weights (`BTC_Model.pth`) and scalers

## Data Source 📊

The project utilizes real-time Bitcoin transaction data from 2021, available on [Kaggle](https://www.kaggle.com/datasets/prasoonkottarathil/btcinusd?select=BTC-Hourly.csv):

## License 📄

This project is licensed under the [Apache License 2.0] - 

## Contact 📧

For any questions or feedback, feel free to reach out to cristianpreguza@gmail.com.

## Acknowledgments 🙏

This project was developed as a technical task for COBBLESTONE ENERGY company.
