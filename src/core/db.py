import mysql.connector
from datetime import datetime

class DBManager:
    def __init__(self, host="localhost", user="root", password="password", database="solar_db"):
        self.config = {
            "host": host,
            "user": user,
            "password": password,
            "database": database
        }
        self.conn = None
        self.cursor = None

    def connect(self):
        try:
            self.conn = mysql.connector.connect(**self.config)
            self.cursor = self.conn.cursor()
            print("Connected to MariaDB/MySQL.")
            self._create_tables()
        except Exception as e:
            print(f"DB Connection Error: {e}")

    def _create_tables(self):
        # Create schema if not exists
        query = """
        CREATE TABLE IF NOT EXISTS metrics (
            id INT AUTO_INCREMENT PRIMARY KEY,
            timestamp DATETIME,
            grid_watts FLOAT,
            load_watts FLOAT,
            pv_watts FLOAT,
            battery_watts FLOAT
        )
        """
        try:
            self.cursor.execute(query)
            self.conn.commit()
        except Exception as e:
            print(f"Table Creation Error: {e}")

    def insert_metrics(self, data):
        if not self.conn or not self.conn.is_connected():
            self.connect()
            if not self.conn: return

        query = """
        INSERT INTO metrics (timestamp, grid_watts, load_watts, pv_watts, battery_watts)
        VALUES (%s, %s, %s, %s, %s)
        """
        values = (
            datetime.now(),
            data.get("grid_watts", 0),
            data.get("load_watts", 0),
            data.get("total_pv_watts", 0),
            data.get("battery_watts", 0)
        )
        try:
            self.cursor.execute(query, values)
            self.conn.commit()
        except Exception as e:
            print(f"Insert Error: {e}")

    def get_daily_aggregates(self):
        # Dummy mock function for UI
        return {
            "Daily Grid kWh": 12.5,
            "Total kWh Used": 15.2,
            "PV kWh Produced": 8.1,
            "Bat Chg/Dis kWh": 4.5,
            "Max Load Day": 3.2,
            "Monthly Summary": 120.4
        }
        
    def close(self):
        if self.cursor: self.cursor.close()
        if self.conn: self.conn.close()
