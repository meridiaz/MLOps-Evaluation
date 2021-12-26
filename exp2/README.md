# Execution of the second experiment

This experiment shows an example on how to use MLflow. Airflow executes all steps between model creation and deployment, automatically.

Three models will be deployed, first one will be deployed as a server and the other two as PyFuncModel. 

To execute the experiment some requirements must be satisfied:
- **Packages and dependencies** . In this case there are two environment .yaml files. aiflow_env.yaml installs dependencies to run aiflow DAG and my_env.yaml file is the one that MLflow uses to run its projects ( you don't have to do it manually). Install dependencies needed to execute airflow DAG automatically by running:
    - `conda env create -f airflow_env.yaml`
    - `conda activate exp2`
- **Airflow first time set up**: the first time running Airflow in a device, the following commands must be run:
    - `airflow db init`
    - `airflow users create --username admin --password admin --role Admin --firstname admin --lastname adminLast --email admin.airflow@gmail.com`
- **Airflow launch**: Then run airflow with the following commands in the conda env created above (called exp2):
    - `airflow webserver`
    - `airflow scheduler`
- **DAG running**: some requeriments must be satisfaced:
    - This experiment assumes that **commands `git init` and `bash src/server_tracking_server.sh` have been executed in the local repository**
    - Move the dag creation file (`src/dag_exp2.py`) and `src/params.yaml` file to ~/airflow/. Unlike the first experiment, this one does not require setting Airflow variables. In this case a params.yaml file.  
    - Replace the email_to_notify_exp2 parameter with the one of your choice in `src/params.yaml` file. 
    - **Choose where do you want to execute this exp by setting path_to_repo_exp2 variable in `src/params.yaml` file.** Make sure this variable indicates the **absolute path** where at least src folder, airflow_env.yaml, my_env.yaml and MLproject files are located.
