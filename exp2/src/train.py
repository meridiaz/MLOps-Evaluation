from mlflow.store.entities.paged_list import T
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
import pandas as pd
import os
import errno

import argparse
import mlflow
from mlflow.models.signature import ModelSignature
from mlflow.types.schema import Schema, ColSpec, TensorSpec


import sklearn.metrics as sk_metrics
import matplotlib.pyplot as plt
import seaborn as sns

def log_metrics(predicted_values, val_y):
    precision = sk_metrics.precision_score(val_y, predicted_values)
    recall = sk_metrics.recall_score(val_y, predicted_values)
    f1 = sk_metrics.f1_score(val_y, predicted_values)
    accuracy = sk_metrics.accuracy_score(val_y, predicted_values)
    mets = {'precision': precision,
                'recall': recall, 
                'f1': f1,
                'accuracy': accuracy
            }
    mlflow.log_metrics(mets)

    # log conf matrix:
    conf_matrix = confusion_matrix(val_y, preds)
    f, ax = plt.subplots()
    sns.heatmap(conf_matrix, annot=True,fmt='g', ax=ax)
    plt.xlabel('Actual')
    plt.ylabel('Predicted')
    plt.title("Confusion Matrix")
    mlflow.log_figure(f, "sklearn_conf_matrix.png")

    return mets

def create_model_signature(val_x):
    list_input = []
    for col, type in zip(val_x.columns, val_x.dtypes):
        if type=="int64":
            type = 'long'
        elif type=="float64":
            type = 'double'
        elif type=='float32':
            type='float'
        elif type=='int32':
            type = 'integer'
        list_input.append(ColSpec(type, col))
    
    input_schema = Schema(list_input)
    output_schema = Schema([ColSpec("integer", "chances")])

    return input_schema, output_schema


parser = argparse.ArgumentParser(description='Process and clean data')
parser.add_argument('--prepared_data', type=str, help='path where training data is located')
parser.add_argument('--train_data', type=str, help='name of the data to be used to train the model')
parser.add_argument('--n_est', type=int, help='number of estimators to pass to the model')
args = parser.parse_args()

path_to_files = args.prepared_data
name_train_data = args.train_data
n_est = args.n_est

if not os.path.isdir(path_to_files):
    raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), path_to_files)

# read data
train_x = pd.read_csv(os.path.join(path_to_files, name_train_data + "-train_x.csv"))
train_y = pd.read_csv(os.path.join(path_to_files, name_train_data + "-train_y.csv"))

# read val data
val_x = pd.read_csv(os.path.join(path_to_files, name_train_data + "-val_x.csv"))
val_y = pd.read_csv(os.path.join(path_to_files, name_train_data + "-val_y.csv"))

with mlflow.start_run():
    clf = RandomForestClassifier(n_estimators=n_est)
    clf.fit(train_x, train_y.values.flatten())

    preds = clf.predict(val_x)    
    metrics = log_metrics(preds, val_y)
    mlflow.log_param('n_est', n_est)
    mlflow.log_param('train_data', name_train_data)
    mlflow.log_param('prepared_data', args.prepared_data)
    

    input_schema, output_schema = create_model_signature(val_x)
    signature = ModelSignature(inputs=input_schema, outputs=output_schema)


    model = mlflow.sklearn.log_model(clf, "sklearn-class-uni", signature=signature) 

        

    

    
