# About this project

Nowadays, there is no common methodology for the creation of machine learning (ML) models and their production deployment in an optimal and automated way. Some companies manage to carry out this process inefficiently and invest large amounts of resources in it.

This project aims to highlight the current situation in which companies find themselves, to analyze the stages that make up the life cycle of an ML model and finally, to propose and clarify the elements, functions and technologies necessary to carry out the above process automatically with almost no manual intervention.

## Contribution of this project
The methodologies and techniques that allow this process to be carried out automatically and an in an optimal way are known as machine learning operations (MLOps).

This project proposes an architecture to create an deploy ML models automatically, see bellow:
![Fully automated high-level process](assets/images/high_level.png "Fully automated process")

Some important elements are:
- **Orchestrated experiment pipeline:** automatically creates models only specifying the model and its parameters.
- **Source code:** in this element you may be thinking this is implemented by git/GitHub, but that's incorrect. GitHub doesn't let you upload large files, so there are other platforms, such as Google Cloud or AWS, that let you upload big files. GitHub is used to track and version metadata and small files, while cloud platforms are used to track model's code and data files.
- **CI:** ensures that all elements are tested before deployment.
- **Packages:** contains everything needed to deploy the pipeline and the model to production.
- **Automated pipeline:** this pipeline automatically deploys the trained models in production and processes the data to be feeded to the model.
- **Model registry:** stores all the versions of the trained models, belonging to a single project, controlling their production deployment.
- **Model catalog:** stores a record of the models of the entire company, indicating the decisions that led to this solution.
- **Performance monitoring:** is responsible for checking that the performance of the deployed models remains above a threshold, otherwise triggers a decision: 1 (retrain deployed model), 2a (create a new model), 2b (change data proccessing in production) or 3 (change inputs of the model deployed).

This project also indicates the software tools that implement each step of the process above, see image bellow:
![Tools that take care of implementing each step](assets/images/tools.png "Tools in fully automated process")

All the tools associated with the concept of MLOps are listed on [this link](https://github.com/EthicalML/awesome-production-machine-learning#model-serving-and-monitoring).

Pipelines are a key concept, they provide a way to automated and modularize tasks in order to build flexible, reusable, easy-to-use and easy-to-debug code.

You can download the full text of the bachelor thesis in the corresponding button of the navigation bar.

### Use cases

Two simple cases have been implemented to illustrate in a practical way some of the above concepts. They can be found in [`exp1`](./exp1.html) and [`exp2`](./exp2.html) folders.

Tools used are [DVC](https://dvc.org/), [MLflow](https://www.mlflow.org/) and [Apache Airflow](https://airflow.apache.org/docs/apache-airflow/stable/index.html)

- [**First use case**](./exp1.html) uses DVC and Apache Airflow. The first one is used to create a pipeline to process raw data and create models. This pipeline can be used to execute some experiments in which you can change some parameters and then you can share them with others. On the other hand, Airflow is used to automate all this process and to provide an interface for managing and visualizing the execution of tasks. Follow [this link](./exp1.html) for more information. 
- [**Second use case**](./exp2.html)  uses MLflow and Apache Airflow. The first one is used to create a pipeline to process raw data and create models, tracking metrics of the created models, store them in a model registry and deploy them locally. Again Airflow is used to automate the process of executing these tasks. Follow [this link](./exp2.html) for more information.

Before executing any of this cases please check `README.md` file of each use case.

### Conclusions

This project concludes with the following:
- Literature does not provide a clear definition of the specific role to be played by each element of the diagram. Some experts propose definitions and guides to fully automated this process, but sometimes they differ slightly from each other.
- In spite of the diagram shown above, there are some funcionality gaps that haven't been yet resolved due to the lack of tools or techniques to address them. These include automatic decision making when the performance of the model falls below a threshold (decisions 1, 2a, 2b and 3) and the implementation of the model catalog.
- Airflow makes it easy to automate and modularize workflows. In addition, it offers a graphical interface that facilitates the management and execution of the different tasks. This makes possible to debug or improve certain tasks.
- DVC is an intuitive and easy-to-use tool, partly due to its strong parallelism with git. It allows versioning large volumes of information such as data and models. However, it is still a growing tool and its user community is small. Also it allows implement the source repository along with git.
-  MLflow is an user-friendly tool that addresses some of the most complex problems that arise, such as making experiments reproducible and packaging the models independently of the library that created them. In addition, it allows you to deploy models on cloud platforms and to feed them with the data for which you want to make predictions in a simple way. 


### Acknowledgments
<table>
  <tr>
<td align="center"><a href="https://github.com/glimmerphoenix"><img src="https://avatars.githubusercontent.com/u/1359409?v=4" height="120" width="100px;" alt=""/><br /><sub><b>Felipe Ortega Soto</b></sub></a><br /><a title="Code">💻</a> <a title="Answering Questions">💬</a> <a title="Documentation">📖</a> <a title="Talks" >📢</a></td>
  
<td align="center"><a href="https://github.com/vmtenorio"><img src="https://github.com/vmtenorio/vmtenorio.github.io/blob/master/images/vmtg.jpg?raw=true" height="120" width="100px;" alt=""/><br /><sub><b>Víctor Manuel Tenorio Gómez</b></sub></a><br /><a title="Code">💻</a> <a title="Answering Questions">💬</a> <a title="Documentation">📖</a> <a title="Reviewed Pull Requests" >👀</a></td>
</tr>  
</table>

