"""
Evaluation utilities: the five metrics and helpers.

Metrics (see thesis Section 4.2.2):
  accuracy, precision, recall, F1-score, ROC-AUC

Requires scikit-learn / numpy.
"""

import numpy as np
from sklearn.metrics import (accuracy_score, precision_score, recall_score,
                             f1_score, roc_auc_score, confusion_matrix,
                             classification_report)


def compute_metrics(y_true, y_pred, y_score=None):
    """Return a dict of the five headline metrics for binary labels {0,1}."""
    m = {
        "accuracy": accuracy_score(y_true, y_pred),
        "precision": precision_score(y_true, y_pred, zero_division=0),
        "recall": recall_score(y_true, y_pred, zero_division=0),
        "f1": f1_score(y_true, y_pred, zero_division=0),
    }
    if y_score is not None:
        try:
            m["roc_auc"] = roc_auc_score(y_true, y_score)
        except ValueError:
            m["roc_auc"] = float("nan")
    else:
        m["roc_auc"] = float("nan")
    return m


def aggregate_folds(fold_metrics):
    """Average a list of metric dicts and also return standard deviations."""
    keys = fold_metrics[0].keys()
    mean = {k: float(np.mean([fm[k] for fm in fold_metrics])) for k in keys}
    std = {k: float(np.std([fm[k] for fm in fold_metrics])) for k in keys}
    return mean, std


def get_confusion(y_true, y_pred):
    return confusion_matrix(y_true, y_pred, labels=[0, 1])


def get_report(y_true, y_pred, target_names=("real", "fake")):
    return classification_report(y_true, y_pred, target_names=list(target_names),
                                 zero_division=0)
