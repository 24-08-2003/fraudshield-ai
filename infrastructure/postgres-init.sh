#!/bin/bash
# Create multiple databases for the stack
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
  CREATE DATABASE mlflow;
  CREATE DATABASE airflow;
  GRANT ALL PRIVILEGES ON DATABASE mlflow TO $POSTGRES_USER;
  GRANT ALL PRIVILEGES ON DATABASE airflow TO $POSTGRES_USER;

  -- Create airflow user for Airflow connections
  DO \$\$
  BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'airflow') THEN
      CREATE USER airflow WITH PASSWORD 'airflow';
    END IF;
  END \$\$;
  GRANT ALL PRIVILEGES ON DATABASE airflow TO airflow;
EOSQL

# Grant schema-level permissions required by PostgreSQL 16+
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "airflow" <<-EOSQL
  GRANT ALL ON SCHEMA public TO airflow;
  GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO airflow;
  ALTER USER airflow CREATEDB;
EOSQL

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "mlflow" <<-EOSQL
  GRANT ALL ON SCHEMA public TO $POSTGRES_USER;
EOSQL
