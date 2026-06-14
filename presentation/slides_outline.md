# Defense Presentation — Speaker Outline (10 slides, ~7–10 min)

Generated file: `Defense_Presentation_Uzbek_Fake_News.pptx`
Rebuild with: `python tools/build_slides.py`

| # | Slide | Talking points (≈ time) |
|---|-------|--------------------------|
| 1 | Title | Greet panel; state title, your name, supervisor. (20s) |
| 2 | Problem & Motivation | Fake news spreads fast; Uzbek is under-served; state the gap. (60s) |
| 3 | Aim, Objectives & Scope | One-sentence aim; 5 SMART objectives; scope excludes deep learning & real-time. (60s) |
| 4 | Literature & Gap | Classical models strong/cheap; no Uzbek baseline exists. (60s) |
| 5 | Methodology & Pipeline | Experimental design; preprocess → TF-IDF → tuned models → 5 metrics. (75s) |
| 6 | Dataset | 4,200 balanced items; sources; ethics; stratified 5-fold CV. (45s) |
| 7 | Results | Walk the table; Linear SVM best (F1 0.912, AUC 0.962); k-NN weakest. (75s) |
| 8 | Discussion | Why linear models win; curse of dimensionality; speed advantage. (60s) |
| 9 | Conclusion & Recommendations | Best model; objectives met; practical + future-work recommendations. (60s) |
| 10 | Thank You / Q&A | Invite questions. (remainder) |

## Likely panel questions — prepared answers
- **Why exclude deep learning?** Scope/time and the need for a transparent, low-cost baseline; noted as future work.
- **Why is SVM best?** TF-IDF is high-dimensional and sparse; margin-based linear separation fits this geometry; k-NN degrades (curse of dimensionality).
- **How did you label fake vs real?** Documented rubric: source reputation + documented falsity; only public text; balanced corpus.
- **Is the result reproducible?** Yes — fixed seed, pinned versions, stratified CV, full code in the repository.
- **Biggest limitation?** Dataset scale and label subjectivity; a larger shared benchmark is the main future step.
