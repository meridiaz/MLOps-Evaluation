import pandas as pd
import os
import mlflow

from json import loads
import requests
import sklearn.metrics as sk_metrics
import subprocess
import psutil
import signal
import yaml

import airflow
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.operators.email import EmailOperator
from airflow import AirflowException


# Vars needed: path_to_repo_exp2 and email_to_notify_exp2
# to set vars copy params.yaml file in ~/airflow/ folder

# it is assume git init command is already run
# and serve_tracking_server.sh is already executed

# check README.md file for more info

DAG_ID = "dag_exp2_tfg_teleco"
EMAILS_TO_NOTIFY = ["example@mail.com", ]

try:
    params = yaml.safe_load(open("params.yaml"))[DAG_ID]["parameters"]
    EMAILS_TO_NOTIFY = [params["email_to_notify_exp2"]]
    PATH_TO_REPO = params["path_to_repo_exp2"]
except FileNotFoundError:
    raise AirflowException('COPY params.yaml FILE TO ~/airflow/ FOLDER')
except KeyError:
    raise AirflowException('MAKE SURE params.yaml FILE HAS DEFINED STAGES: ' + DAG_ID + \
        " AND parameters. ALSO variables path_to_repo_exp2 AND email_to_notify_exp2" + \
        " MUST BE CONFIGURED")


dag = DAG(
    dag_id=DAG_ID,
    schedule_interval='@daily',
    start_date=airflow.utils.dates.days_ago(4), 
    catchup=False, # we dont want to execute every past task
    # the following argument is to notify failure or retry
    default_args={"email": EMAILS_TO_NOTIFY,},
)


def check_path_repo():
    if not os.path.isdir(PATH_TO_REPO):
        raise AirflowException('DEFINE A CORRECT PATH TO LOCAL GIT REPOSITORY')
    if os.system("git -C "+ PATH_TO_REPO+ " rev-parse") != 0:
        raise AirflowException('RUN GIT INIT IN path_to_repo_exp2 or in parent dir ' + \
            'VAR BEFORE EXECUTING THIS EXP')
        
def check_tracking_server():
    try:
        page = requests.get('http://localhost:1240/#/models')
    except requests.exceptions.ConnectionError:
        raise AirflowException('LAUNCH MLFLOW TRACKING SERVER BY RUNNING'+\
         ' bash src/serve_tracking_server.sh FILE')


def _check_prerequisites():
    check_path_repo()
    check_tracking_server()
    
    

check_prerequisites = PythonOperator(         
    task_id="check_prerequisites",   
    python_callable=_check_prerequisites,      
    dag=dag,
)


run_projects = BashOperator(
    task_id="run_projects",
    params={'path_files': PATH_TO_REPO},
    bash_command=(
    """
    export MLFLOW_TRACKING_URI=http://localhost:1240
    echo $MLFLOW_TRACKING_URI

    cd {{params.path_files}}
    # make exps: 
    bash src/exps.sh

    touch .gitignore
    # check if these three patterns are already writen in gitignore file
    grep -qxF 'mlruns/' .gitignore 2>/dev/null || echo 'mlruns/' >> .gitignore
    grep -qxF 'artifacts/' .gitignore 2>/dev/null || echo 'artifacts/' >> .gitignore
    grep -qxF '*.db' .gitignore 2>/dev/null || echo '*.db' >> .gitignore
    
    # commit changes if there is something to commit
    git add src/ MLproject .gitignore my_env.yaml airflow_env.yaml
    git commit -m "Exp2: Added source code, MLproject, and conda envs in yamls files"
    
    """
    ),
    dag=dag,
)


log_models = BashOperator(         
    task_id="log_models",
    params={'path_files': PATH_TO_REPO},
    bash_command=(
    """
    cd {{params.path_files}}
    
    # find best models and register them
    export MLFLOW_TRACKING_URI=http://localhost:1240 &&
    python3 src/log_best_model.py --exp_name 'RF cwurData' &&
    python3 src/log_best_model.py --exp_name 'RF timesData' &&
    python3 src/log_best_model.py --exp_name 'RF shanghaiData'
    
    """
    ), 
    dag=dag,
)


# see: https://www.mlflow.org/docs/latest/models.html#id45
def check_prediction(preds, real, model):
    precision = sk_metrics.precision_score(real, preds)
    recall = sk_metrics.recall_score(real, preds)
    f1 = sk_metrics.f1_score(real, preds)
    accuracy = sk_metrics.accuracy_score(real, preds)
    mets = {'precision': precision,
                'recall': recall, 
                'f1': f1,
                'accuracy': accuracy
            }
    print("Model: "+model.name+" has scored: ")
    print(mets)

    with mlflow.start_run(run_name="Scores of registered models") as active_run:
        mlflow.log_metrics(mets)
        mlflow.log_param("Registered model name", model.name)
        mlflow.set_tag("Run id", model.run_id)
        mlflow.set_tag("Version", model.version)
        mlflow.set_tag("Stage", model.current_stage)


def deploy_command_line(model):

    # run a daemon process to deploy the model
    os.chdir(PATH_TO_REPO)
    os.environ['MLFLOW_TRACKING_URI'] = "http://localhost:1240"
    server = subprocess.Popen("mlflow models serve -m 'models:/"+ \
                model.name+"/Production' --no-conda"
            ,shell=True)
    proc = psutil.Process(server.pid)
    
    # make request:
    tags = model.tags
    headers = {'Content-Type': 'application/json', 'Accept' : 'application/json'}
    response = requests.post('http://localhost:5000/invocations', 
            data=open(os.path.join(tags['prepared_data'], tags['train_data']+"-test_x"), 'rb')
            ,headers=headers)
    
    
    # same as: 
    # os.system("curl http://localhost:5000/invocations -H "+ \
    #            "'Content-type: application/json' -d @"+ \
    #              os.path.join(tags['prepared_data'], tags['train_data']+"-test_x"))
    real = pd.read_json(os.path.join(tags['prepared_data'], tags['train_data']+"-test_y")
                        ,orient='split')

    # exit server and its associated children
    for p in proc.children(recursive=True):
        os.kill(p.pid, signal.SIGINT)

    check_prediction(loads(response.text), real.values.tolist(), model)

def deploy_pyfunc(model, deploy_flavour=False):
    # select model from model registry
    logged_model = 'models:/'+model.name+'/'+model.current_stage
    if deploy_flavour:
        # Load model as a PyFuncModel with flavour .
        loaded_model = mlflow.sklearn.load_model(logged_model)
    else: 
        # Load model as a PyFuncModel.
        loaded_model = mlflow.pyfunc.load_model(logged_model)
    
    # Predict on a Pandas DataFrame. 
    tags = model.tags
    data = pd.read_json(os.path.join(tags['prepared_data'], tags['train_data']+"-test_x")
                        ,orient='split')
    actual = pd.read_json(os.path.join(tags['prepared_data'], tags['train_data']+"-test_y")
                        ,orient='split')
    preds = loaded_model.predict(data)

    check_prediction(preds, actual, model)

    
def _serve_models():

    os.chdir(PATH_TO_REPO)
    os.environ['MLFLOW_TRACKING_URI'] = "http://localhost:1240"
    print(os.getcwd(), flush=True)

    client = mlflow.tracking.MlflowClient()
    registered_models = client.list_registered_models()
    for rm in registered_models:
        if rm == registered_models[0]:
            #serve first model using command line:
            deploy_command_line(rm.latest_versions[-1])
            continue
        # way_to_deploy indicates if a model is served pyfunc or using MLflow flavours
        # it is choosen if the model index id odd or even
        way_to_deploy = bool(registered_models.index(rm) % 2)
        deploy_pyfunc(rm.latest_versions[-1], deploy_flavour=way_to_deploy)



# two different ways of serving: 
# using command line or python API. 
# Second way lets you choose a pyfunc class or a flavour model class.
# Each way lets you select the model from model registry or by run ID 
serve_models = PythonOperator(      
    task_id="serve_models",   
    python_callable=_serve_models,      
    dag=dag,
)


success_email_body = f"""
Hi, <br><br>
Your DAG has been correctly executed.
"""

notify = EmailOperator(
    task_id="notify",
    to=EMAILS_TO_NOTIFY,
    subject="Airflow success: DAG {{dag.dag_id}} correctly executed" + \
            "at {{execution_date.strftime('%Y-%m-%d-%H%M')}}",
    html_content=success_email_body,
    dag=dag,
)

check_prerequisites >> run_projects >> log_models >> serve_models >> notify
