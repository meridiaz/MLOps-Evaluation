import datetime as dt

import os
import git
import re

import airflow
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.operators.email import EmailOperator
from airflow.models import Variable
from airflow import AirflowException

# Vars needed: path_to_repo_exp1, name_repo_ssh, email_to_notify_exp1
# to set vars you must configure them in Admin UI 
# or by command line: airflow variables set key value

# it is assume git init, dvc init and 
# git remote add name_repo_ssh clone-ssh are already done


# following lists contain which branch will be executed
pipe_created = ['execute_experiments', 'download_experiments', 'compare_experiments', 'notify']
pipe_not_created = ['create_dvc_pipeline', 'confirm_changes', 'plot_metrics'] + pipe_created

try:
    Variable.get("email_to_notify_exp1")
except KeyError as e:
    my_var = Variable.set("email_to_notify_exp1", "example@mail.com") 

dag = DAG(
    dag_id="dag_exp1_tfg_teleco",
    schedule_interval='@daily',
    start_date=airflow.utils.dates.days_ago(4), 
    #end_date=dt.datetime(year=2021, month=7, day=15),
    catchup=False, # we dont want to execute every past task
    # the next argument is to notify failure or retry
    default_args={"email": Variable.get("email_to_notify_exp1")},
)


def check_vars_created():
    # check if all vars were created
    try:
        Variable.get("path_to_repo_exp1")
        Variable.get("name_repo_ssh")
    except KeyError as e:
        print('ERR: ' , e)
        raise AirflowException('DEFINE ALL AIRFLOW VARS SPECIFIED IN README.md file')

def check_added_ssh_remote():
    # check if ssh remote was added to git 
    found = False
    pattern = re.compile(r'^git@github.com:.*.git$')
    git_repo = git.Repo(Variable.get("path_to_repo_exp1"), search_parent_directories=True)
    for remote in git_repo.remotes:
        if pattern.match(remote.url):
            found = True
    if not found:
        raise AirflowException('CREATE SSH REMOTE REPO USING: git remote add <name_repo_ssh> <clone link shh>')

def check_path_repo():
    # check if dir exists
    if not os.path.isdir(Variable.get("path_to_repo_exp1")):
        raise AirflowException('DEFINE A CORRECT ABSOLUTE TO EXP1 FOLDER ')
    # check if it a git repo
    if os.system("git -C " +Variable.get("path_to_repo_exp1")+" rev-parse") != 0:
        raise AirflowException('RUN git init IN path_to_repo_exp1 VAR BEFORE EXECUTING THIS EXP')
    if os.system("dvc list .") != 0:
        raise AirflowException('RUN dvc init IN path_to_repo_exp1 VAR BEFORE EXECUTING THIS EXP')
    


def _check_prerequisites():
    check_vars_created()
    check_path_repo()
    check_added_ssh_remote()
    

check_prerequisites = PythonOperator(         
    task_id="check_prerequisites",   
    python_callable=_check_prerequisites,      
    dag=dag,
)

download_data = BashOperator(
    task_id="download_data",
    bash_command=(
    """
    cd {{var.value.path_to_repo_exp1}}
    # if folder does not exit create it
    mkdir -p data/downloaded_data/ && 
    
    # download datasets
    kaggle datasets download mylesoneill/world-university-rankings \
        -p data/downloaded_data/ --unzip -o &&

    # track datasets with dvc
    dvc add data/downloaded_data/ &&

    # check if the donwloaded dataset is the same as the tracked one by dvc
    OUTPUT=$(dvc diff --targets data/downloaded_data/ -- HEAD)
    
    # and with git
    git add data/downloaded_data.dvc data/.gitignore
    git commit -m "Added raw data from kaggle"

    echo $OUTPUT
    """
    ),
    dag=dag,
)

def check_pipeline():
    yaml_path = os.path.join(Variable.get("path_to_repo_exp1"), 'dvc.yaml')
    lock_path = os.path.join(Variable.get("path_to_repo_exp1"), 'dvc.lock')
    yaml_exist = os.path.isfile(yaml_path)
    lock_exist = os.path.isfile(lock_path)

    if yaml_exist and lock_exist:
        return pipe_created
    else:
        if yaml_exist:
            os.remove(yaml_path)
        if lock_exist:
            os.remove(lock_path)
        
    return pipe_not_created
    
    
# this task checks if pipeline is already created
pipeline_is_created = BranchPythonOperator(
    task_id='pipeline_is_created',
    python_callable=check_pipeline,
    do_xcom_push=False
)

create_pipeline = BashOperator(
    task_id="create_dvc_pipeline",
    # modify default settings and retry 2 times after 1 min only in this task
    default_args={'retries': 2, 'retry_delay': dt.timedelta(minutes=1)},
    bash_command=(
        """
    cd {{var.value.path_to_repo_exp1}}
    # setting a default remote locally:
    dvc remote add -d -f localremote ./dvcstore &&

    # tell git we do not want to track plots 
    grep -qxF 'dvcstore/' .gitignore 2>/dev/null || echo 'dvcstore/' >> .gitignore

    dvc run -n featurize \
    -p featurize.world_rank -p featurize.max_rank -p featurize.max_features \
    -d src/featurization.py -d data/downloaded_data \
    -o data/prepared_data \
    python src/featurization.py ./data/downloaded_data/ ./data/prepared_data/ &&

    dvc run -n train \
    -p train.train_data -p train.n_est \
    -d src/train.py -d data/prepared_data/ \
    -o model.pkl \
    python src/train.py ./data/prepared_data/ model.pkl &&

    dvc run -n evaluate \
    -p train.train_data \
    -d src/evaluate.py -d model.pkl -d data/prepared_data/ \
    -M ./evaluation/scores.json \
    --plots-no-cache ./evaluation/prc.json \
    --plots-no-cache ./evaluation/roc.json \
    --plots-no-cache ./evaluation/confu_mat.csv \
    python src/evaluate.py model.pkl \
                 data/prepared_data/ ./evaluation/scores.json \
                 ./evaluation/prc.json ./evaluation/roc.json ./evaluation/confu_mat.csv &&
    
    # the following command should not run the exp because it is already cached
    dvc repro
    dvc dag
    """
    ),
    dag=dag,
)

confirm_changes = BashOperator(
    task_id="confirm_changes",
    bash_command=(
        """
    cd {{var.value.path_to_repo_exp1}}
    # add changes to remote storage
    dvc push model.pkl data/downloaded_data &&
    
    # commit changes to github
    git add src/ dvc.yaml dvc.lock params.yaml .gitignore data/.gitignore ../.dvcignore ../.dvc/config ../.dvc/.gitignore
    git commit -m "Added source code, defined pipeline in DVC and created remote storage"
    dvc remote list
    """
    ),
    dag=dag,
)

plot_metrics = BashOperator(
    task_id="plot_metrics",
    bash_command=(
        """
    cd {{var.value.path_to_repo_exp1}}
    dvc metrics show
    dvc plots show evaluation/confu_mat.csv --template confusion -x actual_chances -y predicted_chances \
                --title "confusion matrix" -o ./dvc_plots/cwurData/conf_mat &&
    dvc plots show -y precision evaluation/prc.json --title "precision plot" \
        -o ./dvc_plots/cwurData/precision &&
    dvc plots show -y recall evaluation/prc.json --title "recall plot" \
        -o ./dvc_plots/cwurData/recall &&
    # save this iteration
    git add evaluation/. params.yaml
    git commit -m "Create evaluation stage"
    
    # check dvc_plots folder
    ls dvc_plots
    """
    ),
    dag=dag,
)

execute_exps = BashOperator(
    task_id="execute_experiments",
    trigger_rule='none_failed_or_skipped',
    bash_command=(
        """
    cd {{var.value.path_to_repo_exp1}}
    # run dvc repro in case some folders may not be in 
    # current workspace
    dvc repro
    # make some experiments
    bash src/exps.sh &&

    dvc exp show --no-pager &&
    # save some of them
    dvc exp push {{var.value.name_repo_ssh}} Snest64 &&
    dvc exp push {{var.value.name_repo_ssh}} Tmr300 &&
    dvc exp push {{var.value.name_repo_ssh}} Sf3 &&
    dvc exp push {{var.value.name_repo_ssh}} Cmr300 &&
    dvc exp list {{var.value.name_repo_ssh}} --all && 
    dvc exp show --no-pager 
    """
    ),
    dag=dag,
)

download_exps = BashOperator(
    task_id="download_experiments",
    bash_command=(
        """
    cd {{var.value.path_to_repo_exp1}}
    # remove experiments
    dvc exp remove --all &&
    # remove cache used in these exps:
    dvc gc -w -f &&


    # download experiments
    dvc exp list {{var.value.name_repo_ssh}} --all &&
    dvc exp pull {{var.value.name_repo_ssh}} Snest64 &&
    dvc exp pull {{var.value.name_repo_ssh}} Tmr300 &&
    dvc exp pull {{var.value.name_repo_ssh}} Sf3 &&
    dvc exp pull {{var.value.name_repo_ssh}} Cmr300 &&

    dvc exp show --no-pager
    """
    ),
    dag=dag,
)

compare_exps = BashOperator(
    task_id="compare_experiments",
    bash_command=(
    """
    cd {{var.value.path_to_repo_exp1}}
    
    # plot differences in saved experiments with git
    # plot sf3 vs snest64 
    dvc params diff Snest64 Sf3 &&
    dvc metrics diff Snest64 Sf3 &&

    dvc plots diff Snest64 Sf3 \
    --targets evaluation/confu_mat.csv \
    --template confusion -x actual_chances -y predicted_chances \
    -o dvc_plots/sf3_vs_snest64/conf_mat &&

    dvc plots diff Snest64 Sf3 \
    --targets ./evaluation/prc.json -y precision \
    -o dvc_plots/sf3_vs_snest64/precision &&

    dvc plots diff Snest64 Sf3 \
    --targets ./evaluation/prc.json -y recall \
    -o dvc_plots/sf3_vs_snest64/recall &&

    dvc exp show --no-pager

    # plot tmr300 vs cwurdata
    dvc params diff Tmr300 &&
    dvc metrics diff Tmr300 &&

    dvc plots diff Tmr300 \
    --targets evaluation/confu_mat.csv \
    --template confusion -x actual_chances -y predicted_chances \
    -o dvc_plots/tmr300_vs_cwurdata/conf_mat &&

    dvc plots diff Tmr300 \
    --targets ./evaluation/prc.json -y precision \
    -o dvc_plots/tmr300_vs_cwurdata/precision &&

    dvc plots diff Tmr300 \
    --targets ./evaluation/prc.json -y recall \
    -o dvc_plots/tmr300_vs_cwurdata/recall &&
                            
    # plot cwurdata vs cmr300
    dvc params diff Cmr300 &&
    dvc metrics diff Cmr300 &&

    dvc plots diff Cmr300 \
    --targets evaluation/confu_mat.csv \
    --template confusion -x actual_chances -y predicted_chances \
    -o dvc_plots/cmr300_vs_cwurdata/conf_mat &&

    dvc plots diff Cmr300 \
    --targets ./evaluation/prc.json -y precision \
    -o dvc_plots/cmr300_vs_cwurdata/precision &&

    dvc plots diff Cmr300 \
    --targets ./evaluation/prc.json -y recall \
    -o dvc_plots/cmr300_vs_cwurdata/recall &&
    
    # delete all exps
    dvc exp remove -g {{var.value.name_repo_ssh}} \
    Snest64 Tmr300 Sf3 Cmr300 &&
    dvc exp remove --all &&
    dvc gc -w -f
    
    """
    ),
    dag=dag,
)

success_email_body = f"""
Hi, <br><br>
Your DAG has been correctly executed.
"""

notify = EmailOperator(
    task_id="notify",
    to=Variable.get("email_to_notify_exp1"),
    subject="Airflow success: DAG {{dag.dag_id}} correctly executed at {{execution_date.strftime('%Y-%m-%d-%H%M')}}",
    html_content=success_email_body,
    dag=dag,
)

check_prerequisites >> download_data >> pipeline_is_created >> [create_pipeline,  execute_exps]
create_pipeline >> confirm_changes >> plot_metrics >> execute_exps >> download_exps >> compare_exps >> notify
execute_exps >> download_exps >> compare_exps >> notify
