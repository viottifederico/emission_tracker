#Importing dataset from sklearn
from sklearn import datasets
from sklearn import metrics
from sklearn import svm
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier

from codecarbon import track_emissions




#Splitting dataset into Training (80%) and testing data (20%) using train_test_split
from sklearn.model_selection import train_test_split

@track_emissions(project_name='XGBoost model', output_file='yearly_log.csv')
def split_data(X, y):
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    return X_train, X_test, y_train, y_test






@track_emissions(project_name='XGBoost model', output_file='yearly_log.csv')
def fit_classifier(x, y, clf):
    clf.fit(x, y)

    return clf

if __name__ == "__main__":
    clf = XGBClassifier()

    iris = datasets.load_iris() #dataset loading
    X = iris.data               #Features stored in X 
    y = iris.target             #Class variable
    # Emulate training for a whole year

    X_train, X_test, y_train, y_test = split_data(X,y)

    for i in range(365):
        trained_clf = fit_classifier(X_train, y_train, clf)