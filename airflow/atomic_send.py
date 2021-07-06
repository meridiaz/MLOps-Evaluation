import datetime as dt
from pathlib import Path

import pandas as pd

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

dag = DAG(
    dag_id="11_atomic_send",
    schedule_interval="@hourly",
    start_date=dt.datetime(year=2021, month=7, day=1),
    #end_date=dt.datetime(year=2021, month=7, day=15),
    #catchup=True,
)

fetch_events = BashOperator(
    task_id="fetch_events",
    bash_command=(
        "mkdir -p /home/meri/airflow/data/events && "
        "echo {{execution_date.strftime('%Y-%m-%d-%H%M')}}.json &&"
        "echo {{next_execution_date.strftime('%Y-%m-%d-%H%M')}}.json &&"
        "echo {{prev_execution_date.strftime('%Y-%m-%d-%H%M')}}.json &&"
        "curl -o /home/meri/airflow/data/events/{{ds}}.json "
        "http://localhost:5000/events?"
        "start_date={{ds}}&"
        "end_date={{next_ds}}"
    ),
    dag=dag,
)


def _calculate_stats(**context):
    """Calculates event statistics."""
    input_path = context["templates_dict"]["input_path"]
    output_path = context["templates_dict"]["output_path"]

    events = pd.read_json(input_path)
    stats = events.groupby(["date", "user"]).size().reset_index()

    Path(output_path).parent.mkdir(exist_ok=True)
    stats.to_csv(output_path, index=False)


calculate_stats = PythonOperator(
    task_id="calculate_stats",
    python_callable=_calculate_stats,
    templates_dict={
        "input_path": "/home/meri/airflow/data/events/{{ds}}.json",
        "output_path": "/home/meri/airflow/data/stats/{{ds}}.csv",
    },
    dag=dag,
)


def email_stats(stats, email):
    """Send an email..."""
    print(f"Sending stats to {email}...")


def _send_stats(email, **context):
    stats = pd.read_csv(context["templates_dict"]["stats_path"])
    email_stats(stats, email=email)


send_stats = PythonOperator(
    task_id="send_stats",
    python_callable=_send_stats,
    op_kwargs={"email": "meritxell.diaz@gmail.com"},
    templates_dict={"stats_path": "/home/meri/airflow/data/stats/{{ds}}.csv"},
    dag=dag,
)

fetch_events >> calculate_stats >> send_stats
