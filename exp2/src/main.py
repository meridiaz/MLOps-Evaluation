import mlflow
import click
from mlflow.utils import mlflow_tags
from mlflow.utils.logging_utils import eprint
from mlflow.entities import RunStatus, experiment
import os

from mlflow.tracking.fluent import _get_experiment_id

def _already_ran(entry_point_name, parameters, git_commit, experiment_id=None):
    """Best-effort detection of if a run with the given entrypoint name,
    parameters, and experiment id already ran. The run must have completed
    successfully and have at least the parameters provided.
    """
    this_file = this_file = os.path.abspath(__file__)

    experiment_id = experiment_id if experiment_id is not None else _get_experiment_id()
    client = mlflow.tracking.MlflowClient()
    #all_run_infos = reversed(client.list_run_infos(experiment_id))
    all_run_infos = client.search_runs([experiment_id])
    for run_info in all_run_infos:
        full_run = client.get_run(run_info.info.run_id)
        tags = full_run.data.tags

        #check if both runs are the same file
        # first check if run has entry point name, if not check if source code file
        # is the same
        # if run has entry point, check if it is equal to the given to this method
        if tags.get(mlflow_tags.MLFLOW_PROJECT_ENTRY_POINT) == None:
            abs_path_run = os.path.abspath(tags.get("mlflow.source.name"))
            if not (os.path.isfile(abs_path_run) and os.path.samefile(this_file, abs_path_run)):
                # not same file
                continue 
        elif tags.get(mlflow_tags.MLFLOW_PROJECT_ENTRY_POINT) != entry_point_name:
            # not same entry point
            continue
        
        # check if running status was not success
        if run_info.info.to_proto().status != RunStatus.FINISHED:
            eprint(
                ("Run not FINISHED, so skipping " "(run_id=%s, status=%s)")
                % (run_info.info.run_id, run_info.info.status)
            )
            continue

        # check if git commit is the same
        previous_version = tags.get(mlflow_tags.MLFLOW_GIT_COMMIT, None)
        if git_commit != previous_version:
            eprint(
                (
                    "Run has a different source version, so skipping "
                    "(found=%s, expected=%s)"
                )
                % (previous_version, git_commit)
            )
            continue
        
        # check if parameters are the same
        match_failed = False
        if parameters.keys() != full_run.data.params.keys():
            continue
        for param_key, param_value in parameters.items():
            run_value = full_run.data.params.get(param_key)
            if os.path.isdir(os.path.abspath(run_value)) and \
                os.path.isdir(os.path.abspath(param_value)):
                # param_key is a path so we need to compare them properly
                if not os.path.samefile(os.path.abspath(run_value), 
                    os.path.abspath(param_value)):
                    match_failed = True
                    break
            elif run_value != str(param_value):
                match_failed = True
                break

        if match_failed:
            continue
        
        return full_run
    eprint("No matching run has been found.")
    return None

def run_entrypoint(entry_point_name, experiment_id, tracking_client, params):
    with mlflow.start_run(nested=True) as child_run:
        p = mlflow.projects.run(
            run_id=child_run.info.run_id,
            uri=".",
            entry_point=entry_point_name,
            parameters=params,
            experiment_id=experiment_id,
            #synchronous=False,
        )
        succeeded = p.wait()
            
        if not succeeded:
            # run failed
            print("FAILED in entrypoint:"+entry_point_name)
            tracking_client.set_terminated(p.run_id, "FAILED")
            return 

        print("SUCCESS in entrypoint:"+entry_point_name)
        if entry_point_name == 'download' or entry_point_name == 'featurization':
            key = list(params.keys())[0]
            mlflow.log_artifact(params[key])
            if  entry_point_name == 'download':
                mlflow.log_param('raw_data', params[key])
                   
                
    return p.run_id

def _get_or_run(entrypoint, exp_id, parameters, git_commit, use_cache):
    tracking_client = mlflow.tracking.MlflowClient()
    existing_run = _already_ran(entrypoint, parameters, git_commit, experiment_id=exp_id)
    if use_cache and existing_run and entrypoint != "download":
        print("Found existing run %s for entrypoint=%s and parameters=%s" % 
                (existing_run.info.run_id, entrypoint, parameters))
        return existing_run
    print("Launching new run for entrypoint=%s and parameters=%s" % (entrypoint, parameters))
    return run_entrypoint(entrypoint, exp_id, tracking_client, parameters)


@click.command(help='This program runs each entry point defined in MLproject file')
@click.option("--raw_data", type=str, help='path where raw data is located')
@click.option("--prepared_data", type=str, help='path where cleaned data is located')
@click.option('--max_rank', type=int, help='max number of universities in each dataset per year')
@click.option('--world_rank', type=int, help='top best universities in each dataset per year')
@click.option('--max_features', type=int, help='max number of features in each dataset')
@click.option("--n_est", type=int, help='number of estimators to pass to the model')
@click.option("--train_data", type=str, help='name of the dataset to be used to train the model')
@click.option('--use_cache', type=bool, help='whether use cache to check repeated runs')

def workflow(raw_data, prepared_data, max_rank, world_rank, 
            max_features, train_data, n_est, use_cache):
    # Note: The entrypoint names are defined in MLproject. The artifact directories
    # are documented by each step's .py file.
    with mlflow.start_run() as active_run:
        # this is the id of the experiment
        exp_id = active_run.info.experiment_id

        git_commit = active_run.data.tags.get(mlflow_tags.MLFLOW_GIT_COMMIT)
        run_id_child = _get_or_run("download", exp_id, {'raw_data': raw_data}, 
                        git_commit, use_cache)
        
        run_id_child = _get_or_run("featurization", exp_id, 
        {
            'prepared_data': prepared_data,
            'raw_data': raw_data,
            'max_rank': max_rank,
            'world_rank': world_rank,
            'max_features': max_features
        }, git_commit, use_cache)

        run_id_child = _get_or_run("train", exp_id, {'train_data': train_data,
            'n_est': n_est, 'prepared_data': prepared_data}, git_commit, use_cache) 
               
    

if __name__ == "__main__":
    workflow()
