


FROM apache/airflow:2.10.5

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt
