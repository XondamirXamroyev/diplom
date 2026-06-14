# Independent Project — Fake News Detection in Uzbek (BTEC Level 6)

This repository contains the complete deliverables for the BTEC Level 6
Independent Project (Unit 2, 70726U):

**"A Comparative Analysis of Classical Machine Learning Models for Fake News
Detection in the Uzbek Language."**

## What's here

| Path | Description |
|------|-------------|
| `thesis/Fake_News_Detection_Uzbek_BTEC_Thesis.docx` | The final thesis (Word, Times New Roman 14, 1.5 spacing) — open and press **F9 / "Update Field"** on the Table of Contents to populate page numbers. |
| `thesis/thesis.md` | The editable Markdown source of the thesis. |
| `presentation/Defense_Presentation_Uzbek_Fake_News.pptx` | The 10-slide defense presentation. |
| `presentation/slides_outline.md` | Speaker notes, timing and likely Q&A. |
| `code/` | The runnable scikit-learn project (preprocessing, 5 models, 5 metrics, figures). See `code/README.md`. |
| `tools/` | Pure-Python generators used to build the `.docx` and `.pptx` (no external libraries required). |

## Regenerate the documents

```bash
# Figures (pure-Python, no matplotlib needed) -> thesis/figures/
python tools/make_figures.py

# Thesis  (.md -> .docx, embeds the figures)
python tools/md2docx.py thesis/thesis.md "thesis/Fake_News_Detection_Uzbek_BTEC_Thesis.docx"

# Presentation
python tools/build_slides.py
```

## Run the experiments

```bash
cd code
pip install -r requirements.txt
python -m src.run_experiments      # ranked results table
python -m src.visualize            # thesis figures -> results/figures/
```

## Key result

The **Linear Support Vector Machine** was the most effective classical model
(F1 ≈ 0.91, ROC-AUC ≈ 0.96), narrowly ahead of Logistic Regression;
k-Nearest Neighbours was clearly weakest on the sparse high-dimensional
TF-IDF representation.

## Before submission — fill in the placeholders

In `thesis/thesis.md` (then recompile) replace: `[Full Name]`, `[ID Number]`,
`[AI — Group Name]`, `[Supervisor Full Name]`, `[Day Month Year]`,
`[XXXX words]`. The same applies to the title and closing slides in
`tools/build_slides.py`.
