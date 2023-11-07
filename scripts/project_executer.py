from logistic_regression_iris_train import fit_classifier as fit_logistic
from xgboost_iris_train import fit_classifier as fit_xbg
from sklearn.model_selection import train_test_split
from sklearn import datasets

from sklearn.linear_model import LogisticRegression
from xgboost import XGBClassifier


from codecarbon import track_emissions


# Load and split the data only once, log it as part of the main process(here considered project)
@track_emissions(project_name='Project Excecuter DataLoad', output_file='yearly_log.csv')
def load_data():
    iris = datasets.load_iris()
    X = iris.data                
    y = iris.target             
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    return X_train, X_test, y_train, y_test

if __name__ == "__main__":

    logistic_reg_clf  =LogisticRegression()
    xgb_clf = XGBClassifier()

    for i in range(365):

        X_train, X_test, y_train, y_test = load_data() # Loading for each iteration to simulate a real daily run
        fit_logistic(X_train, y_train, logistic_reg_clf)
        fit_xbg(X_train, y_train, xgb_clf)

