"""
Model definitions and hyper-parameter search spaces for the five classical
classifiers compared in this project (see thesis Section 4.2.1).

  * Multinomial Naive Bayes
  * Logistic Regression
  * Linear Support Vector Machine
  * Random Forest
  * k-Nearest Neighbours

Each model is paired with a small grid searched by GridSearchCV. The grids are
prefixed with "clf__" because each model is wrapped in a Pipeline whose final
step is named "clf".

Requires scikit-learn.
"""

from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.calibration import CalibratedClassifierCV


def get_models(random_state=42):
    """Return an ordered dict: name -> (estimator, param_grid).

    LinearSVC is wrapped in CalibratedClassifierCV so that predict_proba is
    available for ROC-AUC computation (LinearSVC alone exposes only
    decision_function).
    """
    models = {
        "Multinomial Naive Bayes": (
            MultinomialNB(),
            {"clf__alpha": [0.1, 0.5, 1.0]},
        ),
        "Logistic Regression": (
            LogisticRegression(max_iter=2000, solver="liblinear",
                               random_state=random_state),
            {"clf__C": [0.1, 1.0, 10.0], "clf__penalty": ["l2"]},
        ),
        "Linear SVM": (
            CalibratedClassifierCV(
                LinearSVC(random_state=random_state), cv=3),
            {"clf__estimator__C": [0.1, 1.0, 10.0]},
        ),
        "Random Forest": (
            RandomForestClassifier(random_state=random_state, n_jobs=-1),
            {"clf__n_estimators": [200, 400],
             "clf__max_depth": [None, 50]},
        ),
        "k-Nearest Neighbours": (
            KNeighborsClassifier(metric="cosine"),
            {"clf__n_neighbors": [5, 11, 21]},
        ),
    }
    return models
