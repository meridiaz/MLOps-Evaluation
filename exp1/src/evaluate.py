import pandas as pd
import sys
import yaml
import pickle
import sklearn.metrics as metrics
import json
import math 
import os

# check if args are correct
if len(sys.argv) != 7:
    sys.stderr.write("Arguments error. Usage:\n")
    sys.stderr.write("\tpython evaluate.py model_file path_to_data scores_file prc_file roc_file confusion_mat_file\n")
    sys.exit(1)

params = yaml.safe_load(open("params.yaml"))["train"]

model_file = sys.argv[1]
path_to_files = sys.argv[2] + params['train_data']
scores_file = sys.argv[3]
prc_file = sys.argv[4]
roc_file = sys.argv[5]
conf_file = sys.argv[6] #confusion matrix file

path_to_store_met = scores_file.split('/')[1]

for i in range(3, len(sys.argv)):
    # create dest dir if it does not exit
    if not os.path.isdir(sys.argv[i].split('/')[1]):
        os.mkdir(sys.argv[i].split('/')[1])

# read test data
test_x = pd.read_csv(path_to_files + "-test_x.csv")
test_y = pd.read_csv(path_to_files + "-test_y.csv")

# load model
with open(model_file, "rb") as fd:
    model = pickle.load(fd)

predictions_by_class = model.predict_proba(test_x)
predictions = predictions_by_class[:, predictions_by_class.shape[1]-1]

precision, recall, prc_thresholds = metrics.precision_recall_curve(test_y, predictions)
fpr, tpr, roc_thresholds = metrics.roc_curve(test_y, predictions)

#avg_prec = metrics.average_precision_score(test_y, predictions)
try:
    roc_auc = metrics.roc_auc_score(test_y, predictions)
except ValueError:
    # Only one class in test-y -- cannot calculate ROC AUC
    # Setting to 0
    roc_auc = 0.



# write array in file for future plots:
nth_point = math.ceil(len(prc_thresholds) / 1000)
prc_points = list(zip(precision, recall, prc_thresholds))[::nth_point]

with open(prc_file, "w") as fd:
    json.dump(
        {
            "prc": [
                {"precision": p, "recall": r, "threshold": t}
                for p, r, t in prc_points
            ]
        },
        fd,
        indent=4,
    )

with open(roc_file, "w") as fd:
    json.dump(
        {
            "roc": [
                {"fpr": fp, "tpr": tp, "threshold": t}
                for fp, tp, t in zip(fpr, tpr, roc_thresholds)
            ]
        },
        fd,
        indent=4,
    )

# produce confusion matrix
predicted_values = model.predict(test_x)

confu_mat = test_y.reset_index(drop=True)
confu_mat.rename(columns={'chances': 'actual_chances'}, inplace=True)
confu_mat['predicted_chances'] = pd.Series(predicted_values)
confu_mat.to_csv(conf_file, index=False, index_label=False)

# generate: precision, recall, f1 ands accuracy
precision = metrics.precision_score(test_y, predicted_values)
recall = metrics.recall_score(test_y, predicted_values)
f1 = metrics.f1_score(test_y, predicted_values)
accuracy = metrics.accuracy_score(test_y, predicted_values)

# write metrics in file
with open(scores_file, "w") as fd:
    json.dump({"precision": precision,
                "recall": recall,
                "f1": f1,
                "accuracy": accuracy, 
                "roc_auc": roc_auc}, 
    fd, indent=4)