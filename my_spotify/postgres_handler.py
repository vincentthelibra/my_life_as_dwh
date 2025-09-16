import os
from dotenv import load_dotenv
import psycopg2


class Postgres:
    def __init__(self, env_file=".env"):
        load_dotenv(env_file)

        self.connection_params: dict[str | None, str | None] = {
            "host": os.getenv("POSTGRES_HOST"),
            "database": os.getenv("POSTGRES_DATABASE"),
            "user": os.getenv("POSTGRES_USER"),
            "password": os.getenv("POSTGRES_PASSWORD"),
        }
        self.conn = None

    def connect(self):
        try:
            self.conn = psycopg2.connect(
                host=self.connection_params.get("host"),
                database=self.connection_params.get("database"),
                user=self.connection_params.get("user"),
                password=self.connection_params.get("password"),
            )  # Use dictionary unpacking
            return self.conn
        except psycopg2.Error as e:
            print(f"Error connecting to PostgreSQL: {e}")
            return None

    def close(self):
        if self.conn:
            self.conn.close()

    def execute_query(self, query, params=None):
        if not self.conn:
            print("Not connected to PostgreSQL.")
            return None
        try:
            with self.conn.cursor() as cur:
                cur.execute(query, params)
                self.conn.commit()
                if query.lower().startswith("select"):
                    return cur.fetchall()
        except psycopg2.Error as e:
            self.conn.rollback()
            print(f"Error executing query: {e}")
            return None

    def load_from_file(self, table_name, file_path, delimiter=","):
        table_name = f"bronze.{table_name}"

        if not self.conn:
            print("Not connected to PostgreSQL.")
            return None

        try:
            with self.conn.cursor() as cur:
                with open(file_path, "r") as f:
                    query = f"COPY {table_name} FROM STDIN WITH CSV HEADER DELIMITER '{delimiter}'"
                    cur.copy_expert(query, f)
                self.conn.commit()
                print(f"Successfully loaded data from {file_path} into {table_name}.")
                return True
        except psycopg2.Error as e:
            self.conn.rollback()
            print(f"Error copying from file: {e}")
            return False

    def truncate_table(self, table_name):
        table_name = f"bronze.{table_name}"

        if not self.conn:
            print("Not connected to PostgreSQL.")
            return False
        try:
            with self.conn.cursor() as cur:
                cur.execute(f"TRUNCATE TABLE {table_name} RESTART IDENTITY CASCADE")
                self.conn.commit()
                print(f"Successfully truncated table {table_name}.")
                return True
        except psycopg2.Error as e:
            self.conn.rollback()
            print(f"Error truncating table {table_name}: {e}")
            return False
