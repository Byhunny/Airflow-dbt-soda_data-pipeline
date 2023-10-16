from airflow import DAG
from datetime import datetime

from airflow.utils.task_group import TaskGroup
from cosmos.providers.dbt.dag import DbtDag
from cosmos.providers.dbt import DbtRunOperator
from airflow.datasets import Dataset
from datetime import datetime
from airflow.operators.bash import BashOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator

SODA_PATH = "/usr/local/airflow/include/soda"  # can be specified as an env variable

with DAG(
    dag_id="dwh_layer",
    start_date=datetime(2023, 1, 1),
    schedule=[Dataset(f"SEED://JAFFLE_SHOP")],
    catchup=False,
    max_active_runs=1,
) as dag:
    project_seeds = [
        {
            "project": "dwh_layer",
            "project_dir" : "/usr/local/airflow/dbt_venv/bin/dbt"
        }
    ]
    dwh_layer_transform = DbtRunOperator(
        start_date=datetime(2023, 1, 1),
        task_id="dwh_layer_transform",
        conn_id="postgres",
        project_dir="/usr/local/airflow/dbt/jaffle_shop",
        schema= "public",
        dbt_executable_path = "/usr/local/airflow/dbt_venv/bin/dbt",
        )

    dwh_layer_check = BashOperator(
        task_id="dwh_layer_check",
        bash_command=f"soda scan -d postgres_db -c {SODA_PATH}/configuration.yml {SODA_PATH}/dwh_checks.yml"
    )

    dwh_layer_transform >> dwh_layer_check


