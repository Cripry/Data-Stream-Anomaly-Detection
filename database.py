import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()


class DatabaseHandler:
    def __init__(self):
        load_dotenv()

        self.connection = psycopg2.connect(
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
        )
        self.cursor = self.connection.cursor()

    def create_table(self, table_name, columns):
        """Creates a table in the database with specified columns.

        Args:
            table_name (str): The name of the table to create.
            columns (list): A list of strings representing the column names and data types.
                            Each string should be formatted like:
                            "column_name data_type" (e.g., "Date and Hour VARCHAR(255)")

        Raises:
            psycopg2.errors.SyntaxError: If there's a syntax error in the SQL query.
        """

        # Ensure column definitions include data types
        data_type_columns = []
        for col in columns:
            col_parts = col.split()
            if len(col_parts) != 2:
                raise ValueError(
                    "Invalid column definition. Each column should be formatted as 'name data_type' (e.g., 'Date and Hour VARCHAR(255)')"
                )
            data_type_columns.append(" ".join(col_parts))  # Rejoin with space

        query = f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                {', '.join(data_type_columns)}
            );
        """

        self.cursor.execute(query)
        self.connection.commit()

    def insert_data(self, table_name, data):
        """Inserts a single row of data into the specified table.

        Args:
            table_name (str): The name of the table to insert data into.
            data (dict): A dictionary containing key-value pairs representing column names and their corresponding values.
        """

        columns = ", ".join(data.keys())
        placeholders = ", ".join(["%s"] * len(data))
        query = f"""
            INSERT INTO {table_name} ({columns}) VALUES ({placeholders});
        """
        self.cursor.execute(query, tuple(data.values()))
        self.connection.commit()

    def close_connection(self):
        """Closes the connection to the database."""
        self.cursor.close()
        self.connection.close()

    def fetch_new_data(self, table_name, last_checked_timestamp=None):
        """Retrieves new data from the specified table since the last checked timestamp (optional).

        Args:
            table_name (str): The name of the table to fetch data from.
            last_checked_timestamp (str, optional): A timestamp in the format 'YYYY-MM-DD HH:MM:SS+TZ'
                                                    to filter data newer than this time.

        Returns:
            list: A list of dictionaries representing the fetched data rows.
        """

        query = f"SELECT * FROM {table_name}"
        if last_checked_timestamp:
            query += f" WHERE date > '{last_checked_timestamp}'"

        self.cursor.execute(query)
        columns = [desc[0] for desc in self.cursor.description]
        data = [dict(zip(columns, row)) for row in self.cursor.fetchall()]
        return data

    def update_anomaly_status(self, table_name, date, is_anomaly):
        """Updates the 'isanomaly' column for a specific row in the table.

        Args:
            table_name (str): The name of the table to update.
            date (str): The 'date' value of the row to update.
            is_anomaly (bool): The new anomaly status (True/False).
        """

        query = f"""
            UPDATE {table_name} 
            SET isanomaly = %s 
            WHERE date = %s;
        """
        self.cursor.execute(query, (is_anomaly, date))
        self.connection.commit()
