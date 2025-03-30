# main.py

from datetime import datetime, timedelta       
from airflow import DAG
from airflow.operators.python import PythonOperator

from Extract_and_store import Extract_and_store
from Streaming import stream_data
from Postgresoperator import Postgres
from config import get_api_key 
from airflow.operators.bash import BashOperator



api_key = get_api_key()
extract = Extract_and_store(api_key)
postgres = Postgres('postgres')


default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2025, 3, 21),
    'email_on_failure': False,
    'email_on_retry': False, 
    'retries': 1,
}

with DAG('weather_data_pipeline',
        default_args=default_args,
        schedule = timedelta(minutes=5))as dag:

    extract_data = PythonOperator(
        task_id='extract_and_load_to_postgres', 
        python_callable= extract.load_extracted_to_data_postgres
    )

    load_data = PythonOperator(
        task_id='get_data_from_postgres_to_csv',
        python_callable=postgres.get_data_df,
        op_kwargs={'query': 'SELECT * FROM weather'}
  

    )


    # Replace the Streamlit task with a simple notification
    notification = BashOperator(
        task_id='notification',
        bash_command='echo "Data processing complete. Visit Streamlit at http://localhost:8501"',
        dag=dag,
    )

extract_data >> load_data >> notification


