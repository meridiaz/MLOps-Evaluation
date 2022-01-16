## Second use case

Before executing this experiment check [`exp2/README.m`](https://github.com/meridiaz/MLOps-Evaluation/blob/main/exp2/README.md) file

`exp2` folder constains the following files:
- Raw data downloaded from Kaggle will be located in `data/downloaded_data`. In this case this folder is not ignore in order to show the downloaded files.
- Clean raw data will be located in `data/prepared_data`
- `src` folder contains all source code needed to run the `MLproject` file
- `src/params.yaml` file contains all the configurable parameters needed to execute this experiment, it must be place in ~/airflow/ system folder
- `MLproject` file contains the MLflow project that downloads and process data and builds and evalutes ML models.
- `my_env.yaml` file is the declaration of an Anaconda envivoronment that MLflow needs to execute the `MLproject`file
- `airflow_env.yaml` file is the declaration of an Anaconda envivoronment that must be activate in order to execute this use case
- Note that some files are included in `.gitignore` file such us `artifacts` folder and `.db` files. These files must not be tracked by git because of their size.

### MLflow Demo

Bellow is shown a demo in wich MLflow Tracking, Mflow Models and Mlflow Model Registry modules are shown

![MLflow demo](assets/images/mlflow.gif "MLflow demo")

### Airflow Demo

Bellow is shown a demo in which an Airflow import error is fixed to run this experiment, also this use case DAG is shown

![](assets/images/airflow_exp2.gif "Airflow gif")

[back](./)
