from airflow.providers.postgres.hooks.postgres import PostgresHook
import pandas as pd
from sqlalchemy import create_engine
import os


class Postgres():
    def __init__(self, conn_id: str):
        self.conn_id = conn_id
        self.hook = PostgresHook(self.conn_id)

    def connect(self):
        self.connection = self.hook.get_conn()
        return self.connection

    
    def execute_query(self, query):
        connection = self.connect()
        cursor = self.connection.cursor()
        cursor.execute(query)
        connection.commit()
        cursor.close()

    def get_data_df(self, query):
        self.connect()
        df = pd.read_sql(query, self.connect())
        os.makedirs('data', exist_ok=True)
        df.to_csv('./data/weather.csv', index=False)


    def save_data_to_postgres(self, df, table_name='weather', schema='public', if_exists='replace'):

        conn = self.connect()
        uri = self.hook.get_uri()
        engine = create_engine(uri)
        df.to_sql(table_name, engine, schema=schema, if_exists=if_exists, index=False)
