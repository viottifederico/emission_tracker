from sklearn import datasets
from sklearn import metrics
from sklearn.model_selection import train_test_split
from sklearn import svm
from codecarbon import track_emissions
from sklearn.linear_model import LogisticRegression

@track_emissions(project_name='LogisticRegression model', output_file='yearly_log.csv')
def fit_classifier(x, y, clf):
    clf.fit(x, y)

    return clf

if __name__ == "__main__":
    clf = LogisticRegression()
    iris = datasets.load_iris() 
    X = iris.data               
    y = iris.target             

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Emulate training for a whole year
    for i in range(365):
        trained_clf = fit_classifier(X_train, y_train, clf)