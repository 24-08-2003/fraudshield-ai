FROM apache/airflow:2.9.0-python3.11

USER root
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

USER airflow

COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir \
    mlflow==2.11.1 \
    scikit-learn==1.4.2 \
    xgboost==2.0.3 \
    lightgbm==4.3.0 \
    pandas==2.2.1 \
    numpy==1.26.4 \
    great-expectations==0.18.12 \
    evidently==0.4.24 \
    imbalanced-learn==0.12.0 \
    psycopg2-binary==2.9.9
