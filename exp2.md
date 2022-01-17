## Second use case

Before executing this experiment check [`exp2/README.md`](https://github.com/meridiaz/MLOps-Evaluation/blob/main/exp2/README.md) file

`exp2` folder constains the following files:
- Raw data downloaded from Kaggle will be located in `data/downloaded_data`. In this case this folder is not ignored in order to show the downloaded files.
- Cleaned raw data will be located in `data/prepared_data`
- `src` folder contains all source code needed to run the project defined in `MLproject` file
- `src/params.yaml` file contains all the configurable parameters needed to execute this experiment, must be placed in `~/airflow/` system folder
- `MLproject` file contains the MLflow project that downloads and processes data and builds and evalutes ML models.
- `my_env.yaml` file defines the characteristics and dependencies of an Anaconda envivoronment that MLflow needs to execute the project defined in `MLproject`file
- `airflow_env.yaml` file defines the characteristics and dependencies of an Anaconda envivoronment that must be activated in order to execute this use case
- Note that some files are included in `.gitignore` file such us `artifacts` folder and `.db` files. These files must not be tracked by git because of their size.

### MLflow Demo

Bellow is shown a demo in wich MLflow Tracking, MLflow Models and MLflow Model Registry modules is shown

![MLflow demo](assets/images/mlflow.gif "MLflow demo")

### Airflow Demo

Bellow a demo is shown which an Airflow import error are fixed to run this experiment and the DAG for this use case are shown

![](assets/images/airflow_exp2.gif "Airflow gif")

[back](./)
