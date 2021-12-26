import mlflow
import argparse
from mlflow.store.artifact.runs_artifact_repo import RunsArtifactRepository
from mlflow.exceptions import MlflowException
import os

def change_stage(mv, client, new_stage):
    client.transition_model_version_stage(
        name=mv.name,
        version=mv.version,
        stage=new_stage
    )

def find_best_run(experiment_id, client):
    runs = client.search_runs([experiment_id])
    best_value = 0
    best_run = 0
    for r in runs:
        # check if there metrics were logged in each run
        # and check if each run was running in a project
        if r.data.metrics and sum(r.data.metrics.values()) > best_value \
            and 'mlflow.parentRunId' in r.data.tags.keys() \
            and 'mlflow.project.env' in r.data.tags.keys():
            best_value = sum(r.data.metrics.values())
            best_run = r

    return best_run

def log_tags_registry(metrics, mv, params, client):
    # log tags in model registry
    for met in metrics:
        client.set_model_version_tag(mv.name, mv.version, met, metrics[met])
    for param in params:
        client.set_model_version_tag(mv.name, mv.version, param, params[param])

def register_model(best_run, parent_run, client):
    # Register model name in the model registry
    model_name = 'RFClass-' + best_run.data.params['train_data']
    try:    
        client.create_registered_model(model_name)
    except MlflowException:
        print("Model already exists") 

    # Create a new version of the rfr model under the registered model name
    desc = "RF classifier on " + best_run.data.params['train_data'] + \
                    ". In tags tab metrics and parameters used to create this" + \
                    " model are specified"

    runs_uri = "runs:/{}/sklearn-class-uni".format(best_run.info.run_id)
    model_src = RunsArtifactRepository.get_underlying_uri(runs_uri)
    mv = client.create_model_version(model_name, model_src, best_run.info.run_id, description=desc)

    # print model info
    print("Name: {}".format(mv.name))
    print("Version: {}".format(mv.version))
    print("Description: {}".format(mv.description))
    print("Status: {}".format(mv.status))
    print("Stage: {}".format(mv.current_stage))

    log_tags_registry(best_run.data.metrics, mv, parent_run.data.params, client) 

    return mv

def main():

    parser = argparse.ArgumentParser(description='Find best model in each experiment')
    parser.add_argument('--exp_name', type=str, help='Experiment name where to search', required=True)
    args = parser.parse_args()
    exp_name = args.exp_name
    
    mlflow.set_experiment(exp_name)

    with mlflow.start_run(run_name="Best model") as run:
        experiment_id = run.info.experiment_id
        client = mlflow.tracking.MlflowClient()

        best_run = find_best_run(experiment_id, client)

        if best_run == 0:
            print("ERR: None of the runs of this experiment have stored metrics" + \
                " or none of the runs was running using MLproject")
            os._exit(1)
        # set best params in current run
        mlflow.log_metrics(best_run.data.metrics)
        mlflow.set_tag("best run", best_run.info.run_id)
        mlflow.set_tag("best params", best_run.data.params)
        mlflow.log_param("exp name", exp_name)
        
        
        # get parent run from best run
        parent_run = mlflow.get_run(best_run.data.tags['mlflow.parentRunId'])
        

        # register model logged in best run
        mv = register_model(best_run, parent_run, client)

        # change stage of the model
        change_stage(mv, client, "Production")
        
if __name__ == "__main__":
    main()