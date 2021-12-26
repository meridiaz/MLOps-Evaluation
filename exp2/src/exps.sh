echo $MLFLOW_TRACKING_URI

mlflow run . -P train_data='cwurData' --experiment-name 'RF cwurData'
mlflow run . -P train_data='timesData' --experiment-name 'RF timesData'
mlflow run . -P train_data='shanghaiData' --experiment-name 'RF shanghaiData'

mlflow run . -P train_data='cwurData' -P max_features=3 --experiment-name 'RF cwurData'
mlflow run . -P train_data='timesData' -P max_features=3 --experiment-name 'RF timesData'
mlflow run . -P train_data='shanghaiData' -P max_features=3 --experiment-name 'RF shanghaiData'

mlflow run . -P train_data='cwurData' -P max_rank=300 -P world_rank=150 --experiment-name 'RF cwurData'
mlflow run . -P train_data='timesData' -P max_rank=300 -P world_rank=150 --experiment-name 'RF timesData'
mlflow run . -P train_data='shanghaiData' -P max_rank=300 -P world_rank=150 --experiment-name 'RF shanghaiData'

mlflow run . -P train_data='cwurData' -P n_est=64 --experiment-name 'RF cwurData'
mlflow run . -P train_data='timesData' -P n_est=64 --experiment-name 'RF timesData'
mlflow run . -P train_data='shanghaiData' -P n_est=64 --experiment-name 'RF shanghaiData'


