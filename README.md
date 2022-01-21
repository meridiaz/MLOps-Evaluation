# MLOps-Evaluation

This project shows two simple use cases to apply MLOps principles in an enterprise.  

- `dvc` folder contains some examples on how to use DVC to track large data files.
- `airflow` folder contains some examples on how to implement a simple DAG.
- [`exp1`](https://meridiaz.github.io/MLOps-Evaluation/exp1.html) folder contains the source code for the first use case. It shows how to use DVC along with git to implement the creation of a pipeline which processes the raw data, creates an ML model and evaluates it. Then, DVC is used to run this pipeline several times, with different parameters each time. `src/dag_exp1.py` file is included to show how to automate and visualize these tasks in Apache Airflow tool. Gif below shows a demo of some capabilities of DVC:
![DVC demo](/../gh-pages/assets/images/dvc.gif)
- [`exp2`](https://meridiaz.github.io/MLOps-Evaluation/exp2.html) folder contains the source code for the second use case. It shows how to use MLflow to track experiments, log models in a model registry and serve them via three different methods. Also, `src/dag_exp2.py`file is included to show how to automate and visualize these tasks in Apache Airflow tool. Gif below shows a demo of some capabilities of MLflow:
![MLflow demo](/../gh-pages/assets/images/mlflow.gif) 
- Lastly, this repository contains a `.dvc` folder with some configuration files created by DVC for its proper functioning. 

You can also check [the web page for this project](https://meridiaz.github.io/MLOps-Evaluation/), which reviews the architecture proposed and details for each use case, and you can download [the full PDF Bachelor thesis](/../gh-pages/TFG_Teleco_Meritxell.pdf?raw=true) with a detailed explanation of the concepts involved in this project as well as a detailed explanation and analysis of the use cases previously presented.

