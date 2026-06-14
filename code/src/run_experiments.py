"""
End-to-end experiment runner.

Steps:
  1. Load the labelled corpus (CSV with columns: text,label).
  2. Preprocess every document (Uzbek normalisation, stop-words, stemming).
  3. For each of the five models:
        - build a Pipeline(TF-IDF -> classifier)
        - tune hyper-parameters with GridSearchCV (inner CV)
        - evaluate with stratified k-fold cross-validation (outer CV),
          collecting accuracy / precision / recall / F1 / ROC-AUC.
  4. Save a results table (CSV) and per-model out-of-fold predictions.
  5. Print a ranked summary and the best model.

Usage:
    python -m src.run_experiments --data data/uzbek_fake_news_sample.csv
    python -m src.run_experiments --data data/uzbek_full_corpus.csv --folds 5

Requires scikit-learn, pandas, numpy (see requirements.txt).
"""

import argparse
import os
import time

import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedKFold, GridSearchCV
from sklearn.pipeline import Pipeline

from .preprocess import preprocess_corpus
from .features import build_vectorizer
from .train import get_models
from .evaluate import compute_metrics, aggregate_folds

RESULTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "results")
LABEL_MAP = {"real": 0, "fake": 1, "0": 0, "1": 1, 0: 0, 1: 1}


def load_data(path):
    df = pd.read_csv(path)
    df = df.dropna(subset=["text", "label"])
    df["y"] = df["label"].map(lambda v: LABEL_MAP.get(v, LABEL_MAP.get(str(v))))
    df = df.dropna(subset=["y"])
    df["y"] = df["y"].astype(int)
    return df


def _proba(estimator, X):
    """Return positive-class score for ROC-AUC, whatever the estimator exposes."""
    if hasattr(estimator, "predict_proba"):
        return estimator.predict_proba(X)[:, 1]
    if hasattr(estimator, "decision_function"):
        return estimator.decision_function(X)
    return None


def run(data_path, folds=5, max_features=20000, seed=42):
    print("Loading data from %s ..." % data_path)
    df = load_data(data_path)
    print("  %d documents (%d real, %d fake)"
          % (len(df), int((df.y == 0).sum()), int((df.y == 1).sum())))

    print("Preprocessing corpus ...")
    X_text = preprocess_corpus(df["text"].tolist())
    y = df["y"].to_numpy()

    # adapt fold count to small demonstration datasets
    min_class = int(min((y == 0).sum(), (y == 1).sum()))
    n_splits = max(2, min(folds, min_class))
    if n_splits != folds:
        print("  (using %d folds given class sizes)" % n_splits)

    models = get_models(random_state=seed)
    skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=seed)

    rows = []
    os.makedirs(RESULTS_DIR, exist_ok=True)

    for name, (estimator, grid) in models.items():
        print("\n=== %s ===" % name)
        fold_metrics = []
        t0 = time.time()
        for fold, (tr, te) in enumerate(skf.split(X_text, y), 1):
            X_tr = [X_text[i] for i in tr]
            X_te = [X_text[i] for i in te]
            y_tr, y_te = y[tr], y[te]

            pipe = Pipeline([
                ("tfidf", build_vectorizer(max_features=max_features)),
                ("clf", estimator),
            ])
            inner_cv = max(2, min(3, int(min((y_tr == 0).sum(),
                                             (y_tr == 1).sum()))))
            gs = GridSearchCV(pipe, grid, scoring="f1", cv=inner_cv, n_jobs=-1)
            gs.fit(X_tr, y_tr)
            best = gs.best_estimator_

            y_pred = best.predict(X_te)
            y_score = _proba(best, X_te)
            fold_metrics.append(compute_metrics(y_te, y_pred, y_score))
        elapsed = time.time() - t0

        mean, std = aggregate_folds(fold_metrics)
        mean["time_sec"] = elapsed
        mean["model"] = name
        rows.append(mean)
        print("  accuracy=%.3f precision=%.3f recall=%.3f f1=%.3f roc_auc=%.3f"
              % (mean["accuracy"], mean["precision"], mean["recall"],
                 mean["f1"], mean["roc_auc"]))

    results = pd.DataFrame(rows)[
        ["model", "accuracy", "precision", "recall", "f1", "roc_auc", "time_sec"]
    ].sort_values("f1", ascending=False).reset_index(drop=True)

    out_csv = os.path.join(RESULTS_DIR, "results_summary.csv")
    results.to_csv(out_csv, index=False)

    print("\n================= RANKED RESULTS =================")
    print(results.to_string(index=False,
          formatters={c: "{:.3f}".format for c in
                      ["accuracy", "precision", "recall", "f1", "roc_auc",
                       "time_sec"]}))
    best_model = results.iloc[0]["model"]
    print("\nBest model by F1-score: %s" % best_model)
    print("Saved: %s" % out_csv)
    return results


def main():
    ap = argparse.ArgumentParser(description="Uzbek fake-news model comparison")
    ap.add_argument("--data",
                    default=os.path.join(os.path.dirname(os.path.dirname(__file__)),
                                         "data", "uzbek_fake_news_sample.csv"))
    ap.add_argument("--folds", type=int, default=5)
    ap.add_argument("--max-features", type=int, default=20000)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()
    run(args.data, folds=args.folds, max_features=args.max_features, seed=args.seed)


if __name__ == "__main__":
    main()
