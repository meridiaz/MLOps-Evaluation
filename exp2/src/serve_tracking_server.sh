#!/usr/bin/env sh

export MLFLOW_TRACKING_URI=http://localhost:1240
echo $MLFLOW_TRACKING_URI

# store entities in mlflow.db in order to use model registry
mlflow server \
--backend-store-uri sqlite:///mlflow.db \
--default-artifact-root ./artifacts \
--host 0.0.0.0 \
--port 1240
