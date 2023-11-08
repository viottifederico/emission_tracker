# Emission_tracker
### **Emission_tracker** tool to represent emission of python code in a dashboard

### The project is separeted in two main modules

1. The `notebooks` folder
    - Contains two notebooks examples making use of the emission tracker. 
        - The `xgboost-implementation-on-iris-dataset-python.ipynb` notebook has an XGBoost training example for the iris dataset, in which the logs are saved on the default file `emissions.csv`
        - The `01_cifar10_tinyvgg.ipynb` contains a training example that trains a simple mini vgg convolutonal neural network on the cifar dataset. This notebook makes use of hardware acceleration, using both CUDA and mps(Metal Performance Shaders on Apple Silicon) if any of those if available.

2. The `scripts` folder 
    - This folder contains different script modules as follows:
        - `logistic_regression_iris_train.py` which includes a simple logistic regression train using sklearn and logs the power consumption using `code carbon`.
        - `xgboost_iris_train.py` which trains an XGBoost Classifier on the iris dataset, also it logs the power consumption using `code carbon`. This script emulates two steps, loading and training
        - `project_executer.py` makes use of both the previous scripts and emulates a training situation with 3 steps, loading and training both the available models.
    - All the `code carbon` logs are saved on the `yearly_log.csv` file on the same folder.