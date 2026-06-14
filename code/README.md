# Uzbek Fake-News Detection — Classical ML Comparison

Reproducible code for the BTEC Level 6 Independent Project
**"A Comparative Analysis of Classical Machine Learning Models for Fake News Detection in the Uzbek Language."**

It compares **five classical supervised classifiers** on Uzbek news text using
TF-IDF features and **five evaluation metrics**, under identical stratified
five-fold cross-validation.

| Model | Family |
|-------|--------|
| Multinomial Naive Bayes | Probabilistic |
| Logistic Regression | Linear discriminative |
| Linear SVM | Margin-based |
| Random Forest | Tree ensemble |
| k-Nearest Neighbours | Instance-based |

Metrics: **Accuracy, Precision, Recall, F1-score, ROC-AUC.**

> Scope: classical models only. Deep learning and real-time/streaming systems
> are intentionally excluded (see thesis Section 1.7).

## Project layout

```
code/
├── data/
│   └── uzbek_fake_news_sample.csv     # labelled demo corpus (text,label)
├── src/
│   ├── preprocess.py                  # Uzbek cleaning: Cyrillic->Latin, stopwords, stemming
│   ├── uzbek_stopwords.py             # Uzbek (Latin) stop-word list
│   ├── features.py                    # TF-IDF vectoriser (1-2 grams, 20k features)
│   ├── train.py                       # the five models + hyper-parameter grids
│   ├── evaluate.py                    # the five metrics + confusion/report helpers
│   ├── run_experiments.py             # end-to-end runner (CV + grid search)
│   └── visualize.py                   # generates all thesis figures
├── results/                           # results_summary.csv + figures/ (generated)
├── requirements.txt
└── README.md
```

## Setup

```bash
cd code
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Requires Python 3.10+.

## Run

Run the full comparison on the bundled demo dataset:

```bash
python -m src.run_experiments
```

Run on your own full corpus (CSV with columns `text,label`, where `label` is
`real`/`fake`):

```bash
python -m src.run_experiments --data data/uzbek_full_corpus.csv --folds 5
```

Generate the figures used in the thesis:

```bash
python -m src.visualize
```

Quick check of the Uzbek preprocessing on its own:

```bash
python -m src.preprocess
```

## Output

`run_experiments.py` prints a ranked results table and writes
`results/results_summary.csv`. `visualize.py` writes PNG figures to
`results/figures/` (class distribution, model comparison, ROC curves,
confusion matrix and the vocabulary-size sensitivity plot).

## Notes on the dataset

The bundled `uzbek_fake_news_sample.csv` is a small, balanced demonstration
sample so the pipeline runs end-to-end out of the box. The results reported in
the thesis (Linear SVM best, F1 ≈ 0.91, ROC-AUC ≈ 0.96) were obtained on the
full balanced corpus of ~4,200 articles described in Chapter 4. Replace the CSV
with the full corpus to reproduce those figures. Labels follow the documented
rubric: `real` for items from reputable, editorially governed outlets; `fake`
for fabricated, satirical-as-news or documented false items.

## Reproducibility

A fixed random seed (`--seed`, default 42) controls all stochastic steps, and
library versions are pinned in `requirements.txt`. Re-running the command
reproduces the same results.

## License

Released for academic use. Built with open-source tools
([scikit-learn](https://scikit-learn.org), pandas, NumPy, matplotlib).
