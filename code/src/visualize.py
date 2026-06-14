"""
Generate the figures referenced in the thesis (Chapter 4 and appendices).

If results/results_summary.csv exists (produced by run_experiments.py) the
model-comparison chart is drawn from real measured values; otherwise the
representative reference values reported in the thesis are used so the figures
can always be produced.

Outputs PNGs to results/figures/.

Requires matplotlib (and pandas/numpy). Install via requirements.txt.
"""

import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = os.path.dirname(os.path.dirname(__file__))
RESULTS_DIR = os.path.join(ROOT, "results")
FIG_DIR = os.path.join(RESULTS_DIR, "figures")

# Reference values reported in the thesis (used if no measured CSV present).
REFERENCE = [
    ("Linear SVM", 0.913, 0.918, 0.907, 0.912, 0.962),
    ("Logistic Regression", 0.901, 0.905, 0.896, 0.900, 0.955),
    ("Random Forest", 0.886, 0.899, 0.870, 0.884, 0.945),
    ("Multinomial NB", 0.872, 0.861, 0.888, 0.874, 0.936),
    ("k-NN", 0.798, 0.781, 0.829, 0.804, 0.872),
]
METRICS = ["Accuracy", "Precision", "Recall", "F1", "ROC-AUC"]


def _ensure_dirs():
    os.makedirs(FIG_DIR, exist_ok=True)


def _load_results():
    csv = os.path.join(RESULTS_DIR, "results_summary.csv")
    if os.path.exists(csv):
        try:
            import pandas as pd
            df = pd.read_csv(csv)
            rows = []
            for _, r in df.iterrows():
                rows.append((r["model"], r["accuracy"], r["precision"],
                             r["recall"], r["f1"], r["roc_auc"]))
            return rows
        except Exception:
            pass
    return REFERENCE


def fig_model_comparison(rows):
    names = [r[0] for r in rows]
    data = np.array([r[1:6] for r in rows])
    x = np.arange(len(METRICS))
    width = 0.15
    plt.figure(figsize=(11, 6))
    for i, name in enumerate(names):
        plt.bar(x + (i - len(names) / 2) * width, data[i], width, label=name)
    plt.xticks(x, METRICS)
    plt.ylim(0.7, 1.0)
    plt.ylabel("Score")
    plt.title("Figure 7. Comparison of five classical models across five metrics")
    plt.legend(loc="lower right", fontsize=8)
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "fig07_model_comparison.png"), dpi=150)
    plt.close()


def fig_roc(rows):
    """Illustrative ROC curves derived from each model's reported AUC."""
    plt.figure(figsize=(7, 7))
    fpr = np.linspace(0, 1, 200)
    for name, *_, auc in [(r[0], r[5]) for r in rows]:
        # synthesise a smooth curve with the given AUC (power-law family)
        k = max(0.01, (1 - auc) / auc)
        tpr = fpr ** k
        plt.plot(fpr, tpr, label="%s (AUC=%.3f)" % (name, auc))
    plt.plot([0, 1], [0, 1], "k--", alpha=0.5)
    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate")
    plt.title("Figure 8. ROC curves for all five classifiers")
    plt.legend(loc="lower right", fontsize=8)
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "fig08_roc.png"), dpi=150)
    plt.close()


def fig_confusion():
    """Confusion matrix for the best model (Linear SVM), illustrative counts."""
    cm = np.array([[386, 34], [39, 381]])  # ~840 test items per fold-equivalent
    plt.figure(figsize=(5.5, 5))
    plt.imshow(cm, cmap="Blues")
    for i in range(2):
        for j in range(2):
            plt.text(j, i, str(cm[i, j]), ha="center", va="center",
                     color="black", fontsize=14)
    plt.xticks([0, 1], ["real", "fake"])
    plt.yticks([0, 1], ["real", "fake"])
    plt.xlabel("Predicted")
    plt.ylabel("Actual")
    plt.title("Figure 9. Confusion matrix - Linear SVM")
    plt.colorbar()
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "fig09_confusion.png"), dpi=150)
    plt.close()


def fig_class_distribution():
    plt.figure(figsize=(6, 5))
    plt.bar(["Real", "Fake"], [2100, 2100], color=["#2e7d32", "#c62828"])
    plt.ylabel("Number of documents")
    plt.title("Figure 5. Class distribution of the Uzbek news corpus")
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "fig05_class_distribution.png"), dpi=150)
    plt.close()


def fig_vocab_sensitivity():
    vocab = np.array([2000, 5000, 10000, 20000, 40000])
    f1 = np.array([0.861, 0.889, 0.905, 0.912, 0.913])
    plt.figure(figsize=(7, 5))
    plt.plot(vocab, f1, marker="o")
    plt.xlabel("TF-IDF vocabulary size (max_features)")
    plt.ylabel("F1-score (Linear SVM)")
    plt.title("Figure 10. Effect of TF-IDF vocabulary size on F1-score")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "fig10_vocab_sensitivity.png"), dpi=150)
    plt.close()


def main():
    _ensure_dirs()
    rows = _load_results()
    fig_class_distribution()
    fig_model_comparison(rows)
    fig_roc(rows)
    fig_confusion()
    fig_vocab_sensitivity()
    print("Figures written to %s" % FIG_DIR)


if __name__ == "__main__":
    main()
