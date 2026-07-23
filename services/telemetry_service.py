import sqlite3
import pandas as pd


class TelemetryService:


    def __init__(self, db_path="data/f1_data.db"):
        self.db_path = db_path

    def get_connection(self):
        return sqlite3.connect(self.db_path)
    
    def get_available_sessions(self):
        with self.get_connection() as conn:
            query = """
            SELECT name
            FROM sqlite_master
            WHERE type='table'
            AND name != 'calendar'
            """

            tables = pd.read_sql(query, conn)

        return tables["name"].tolist()
    
    def load_raw_telemetry(self, table_name):
        with self.get_connection() as conn:
            try:
                return pd.read_sql(
                f"SELECT * FROM {table_name}",
                conn
                )
            except Exception as e:
                raise ValueError(
                    f"Unable to load telemetry table '{table_name}'"
                ) from e
        
    def process_telemetry(self, df):
        df = df.copy()
        df.columns = [c.capitalize() for c in df.columns]
        df["Time"] = pd.to_numeric(
            df["Time"],
            errors="coerce"
        )

        df["Speed_ms"] = df["Speed"] / 3.6

        dt = df["Time"].diff().fillna(0.1)

        df["Distance"] = (
        df["Speed_ms"] * dt
        ).cumsum()

        acceleration = (
            df["Speed_ms"].diff() /
            dt.replace(0, 0.1)
        )

        df["G_Long"] = acceleration / 9.81

        return df
    
    def get_processed_telemetry(self, table_name):
        raw = self.load_raw_telemetry(table_name)
        return self.process_telemetry(raw)