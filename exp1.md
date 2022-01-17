## First use case

Before executing this experiment check [`exp1/README.md`](https://github.com/meridiaz/MLOps-Evaluation/blob/main/exp1/README.md) file.

`exp1` folder contains the following files:
- Raw data downloaded from Kaggle will be located in `data/downloaded_data`
- Clean raw data will be located in `data/prepared_data`
- `dvc_plots` folder contains some examples of plots created by DVC 
- `evaluation` folder contains all metrics and JSON files used by DVC in creating those plots
- `src` folder contains all the source code needed to run the pipeline
- `params.yaml` file contains all the configurable parameters for processing the data and creating the model
- `dvc.yaml` file is the declaration of the DVC pipeline, while `dvc.lock`file contain metadata used by DVC to track pipeline's output files
- `my_env.yaml` file defined the characteristics and dependencies of an Anaconda envivoronment that must be activated in order to correctly execute this use case
- Note that, by default, DVC creates a local `.gitignore` file to ignore big files that must not be tracked by git, such as model.pkl and `data/downloaded_data` folder

### DVC Demo

Here, a demo is shown in which two experiments are executed. One of them in a temp dir and the other one in the workspace. Then one of them is uploaded to the git remote and deleted from workspace. After that, it is downloaded from the git remote back to workspace

![DVC demo](assets/images/dvc.gif "DVC demo")

### Airflow screenshoots and Demo

In this demo Airflow`s home page with all created DAGs, exp1 DAG with some logs and all Airflow variables needed to run this use case are shown.

![](assets/images/airflow_exp1.gif "Airflow gif")

Bellow, some images with the status of tasks are shown. This status depends on which branch of the DAG is executed.
![](assets/images/captura_dag_rama1.png "Airflow screenshot")

![](assets/images/captura_dag_rama2.png "Airflow screenshot")

[back](./)
