from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
import pandas as pd
import yaml
import glob
import pickle
import sys
import os

if len(sys.argv) != 3:
    sys.stderr.write("Arguments error. Usage:\n")
    sys.stderr.write("\tpython train.py features model\n")
    sys.exit(1)

input = sys.argv[1]
output = sys.argv[2]

params = yaml.safe_load(open("params.yaml"))["train"]
path_to_files = input
train_data = params['train_data']

# read data
train_x = pd.read_csv(os.path.join(path_to_files, train_data+"-train_x.csv"))
train_y = pd.read_csv(os.path.join(path_to_files, train_data+"-train_y.csv"))

clf = RandomForestClassifier(n_estimators=params['n_est'])
clf.fit(train_x, train_y.values.flatten())


with open(output, "wb") as fd:
    pickle.dump(clf, fd)