import datetime as dt
from pathlib import Path

import pandas as pd

import airflow
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.operators.email import EmailOperator


files_path = "/home/meri/Escritorio/tfg/teleco/MLOps-Evaluation/airflow/"

dag = DAG(
    dag_id="tfg_teleco_dag1",
    schedule_interval=None, #de momento lo dejo a none#"@hourly",
    start_date=airflow.utils.dates.days_ago(14), #lo defino asi para no tener que cambiarlo
    #end_date=dt.datetime(year=2021, month=7, day=15),
    #catchup=True,
)

#descargo el dataset que me interesa de kaggle
#Es necesario tener instalado previamente kaggle
download_dataset = BashOperator(
    task_id="download_dataset",
    bash_command=(
        "kaggle datasets download shivamb/netflix-shows -p " + files_path + " --unzip -o"
    ),
    dag=dag,
)


def _join_datasets(input_path1, input_path2, output_path):
    
    #input_path = context["templates_dict"]["input_path"]
    data1 = pd.read_csv(input_path1)
    data2 =  pd.read_csv(input_path2)

    data3 = data1.join(data2.set_index("title"), on="title")
    
    Path(output_path).parent.mkdir(exist_ok=True)
    data3.to_csv(path_or_buf=output_path)


join_datasets = PythonOperator(
    task_id="join_datasets",
    python_callable=_join_datasets,
    op_kwargs={
    		"input_path1": files_path+"netflix_titles.csv", 
    		"input_path2": files_path+"dataset_info_adicional.csv",
    		"output_path": files_path+"join_datasets.csv",
    		},
    dag=dag,
)


notify = EmailOperator(
    task_id="notify",
    to="meritxell.diaz@gmail.com",
    subject="notify success dag",
    html_content="<h3>your tasks have been executed correctly</h3>",
    dag=dag,
)

download_dataset >> join_datasets >> notify
