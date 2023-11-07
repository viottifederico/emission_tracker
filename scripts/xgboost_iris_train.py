#Importing dataset from sklearn
from sklearn import datasets
from sklearn import metrics

iris = datasets.load_iris() #dataset loading
X = iris.data               #Features stored in X 
y = iris.target             #Class variable

#Splitting dataset into Training (80%) and testing data (20%) using train_test_split
from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)


#Create an XGB classifier and instance of the same
from sklearn import svm
from xgboost import XGBClassifier
clf = XGBClassifier()

from codecarbon import track_emissions


@track_emissions(project_name='XGBoost model')
def fit_classifier(x, y, clf):
    clf.fit(x, y)

    return clf

# Emulate training for a whole year
for i in range(365):
    trained_clf = fit_classifier(X_train, y_train, clf)