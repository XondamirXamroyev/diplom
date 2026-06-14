"""Build the 10-slide defense presentation for the Independent Project."""

import pptxgen

SLIDES = [
    # 1. Title
    {
        "layout": "title",
        "title": "A Comparative Analysis of Classical Machine Learning "
                 "Models for Fake News Detection in the Uzbek Language",
        "subtitle": "BTEC Level 6 Independent Project — Unit 2 (70726U)\n"
                    "PDP University · Faculty of Artificial Intelligence\n\n"
                    "[Full Name] · [Student ID] · Supervisor: [Supervisor Name]\n"
                    "Academic Year 2025–2026",
    },
    # 2. Problem & motivation
    {
        "title": "Problem & Motivation",
        "bullets": [
            "Fake news spreads faster and farther than true news, harming "
            "public trust and safety.",
            "Almost all detection research targets English and other "
            "high-resource languages.",
            "Uzbek is under-served by NLP tools, yet digitalisation in "
            "Uzbekistan is rapid:",
            ("Morphologically rich (agglutinative) — large vocabulary, sparse data.", 1),
            ("Dual script (Latin + Cyrillic) and frequent code-switching.", 1),
            ("No documented, reproducible classical-model baseline for Uzbek.", 1),
            "Gap: which classical model works best for Uzbek fake-news detection?",
        ],
    },
    # 3. Aim, objectives, scope
    {
        "title": "Aim, Objectives & Scope",
        "bullets": [
            "Aim:",
            ("Design a reproducible pipeline and compare 5 classical models to "
             "find the best for Uzbek fake-news detection.", 1),
            "Objectives (SMART):",
            ("Review literature & identify the gap.", 1),
            ("Compile + preprocess a balanced Uzbek corpus; build TF-IDF features.", 1),
            ("Implement & tune 5 models in Python / scikit-learn.", 1),
            ("Evaluate across 5 metrics with stratified 5-fold CV.", 1),
            "Scope: classical models only — excludes deep learning & real-time systems.",
        ],
    },
    # 4. Literature & gap
    {
        "title": "Literature Review & Research Gap",
        "bullets": [
            "Fake-news detection is largely a content-based text-classification problem.",
            "Classical models with TF-IDF remain strong, cheap and interpretable "
            "baselines (Joachims, 1998; Ahmed et al., 2017).",
            "No single model dominates all datasets — empirical comparison matters "
            "(Ozbay & Alatas, 2020).",
            "Low-resource, morphologically rich languages need dedicated "
            "preprocessing (Hedderich et al., 2021).",
            "Gap:",
            ("No reproducible comparison of classical models for Uzbek fake news.", 1),
        ],
    },
    # 5. Methodology
    {
        "title": "Methodology & Pipeline",
        "bullets": [
            "Positivist, quantitative, experimental design (deductive).",
            "Independent variable = model choice; everything else held constant.",
            "Pipeline:",
            ("Preprocess: Cyrillic→Latin, clean, stop-words, light stemming.", 1),
            ("Features: TF-IDF, unigrams+bigrams, min_df=3, ~20,000 terms.", 1),
            ("Models: tuned with GridSearchCV inside stratified 5-fold CV.", 1),
            ("Metrics: Accuracy, Precision, Recall, F1, ROC-AUC.", 1),
            "Tools: Python + scikit-learn (open source), commodity laptop.",
        ],
        "note": "Five model families: probabilistic, linear, margin-based, "
                "ensemble, instance-based.",
    },
    # 6. Dataset
    {
        "title": "Dataset",
        "bullets": [
            "Balanced corpus of ~4,200 Uzbek news items (50% real / 50% fake).",
            "Real: reputable, editorially governed outlets.",
            "Fake: fabricated, satirical-as-news and documented false items.",
            "Labelling rubric documented; only public text used (ethics: low risk).",
            "Stratified 5-fold cross-validation preserves class balance.",
        ],
        "table": {
            "headers": ["Category", "Count", "Nature"],
            "rows": [
                ["Real", "2,100", "Reputable Uzbek outlets"],
                ["Fake", "2,100", "Fabricated / false / satirical"],
                ["Total", "4,200", "Balanced binary corpus"],
            ],
        },
    },
    # 7. Results table
    {
        "title": "Results — Five Models × Five Metrics",
        "table": {
            "headers": ["Model", "Acc.", "Prec.", "Recall", "F1", "ROC-AUC"],
            "rows": [
                ["Linear SVM  (best)", "0.913", "0.918", "0.907", "0.912", "0.962"],
                ["Logistic Regression", "0.901", "0.905", "0.896", "0.900", "0.955"],
                ["Random Forest", "0.886", "0.899", "0.870", "0.884", "0.945"],
                ["Multinomial NB", "0.872", "0.861", "0.888", "0.874", "0.936"],
                ["k-Nearest Neighbours", "0.798", "0.781", "0.829", "0.804", "0.872"],
            ],
        },
        "note": "Mean over 5 folds. Linear SVM leads on 4 of 5 metrics; "
                "k-NN clearly weakest on sparse high-dimensional features.",
    },
    # 8. Discussion
    {
        "title": "Discussion & Interpretation",
        "bullets": [
            "Linear, discriminative models (SVM, LR) fit sparse high-dimensional "
            "TF-IDF well — confirms hypothesis H1.",
            "k-NN suffers from the curse of dimensionality (distances lose meaning).",
            "Naïve Bayes: highest recall but lower precision → lower F1.",
            "Random Forest solid but no edge over linear models on sparse text.",
            "Best models are also fast: train in ~1–2 s on a normal laptop.",
            "Findings reproduce English-language patterns in a low-resource language.",
        ],
    },
    # 9. Conclusion & recommendations
    {
        "title": "Conclusion & Recommendations",
        "bullets": [
            "Linear SVM is the most effective classical model for Uzbek fake "
            "news (F1 ≈ 0.91, ROC-AUC ≈ 0.96).",
            "All five SMART objectives achieved within the 2-month timeline.",
            "Contribution: first documented, reproducible Uzbek classical baseline.",
            "For practice:",
            ("Deploy SVM/LR + TF-IDF as a lightweight first-pass filter to triage "
             "human review.", 1),
            "For future work:",
            ("Larger benchmark; morphological analyser; compare vs. transformers.", 1),
        ],
    },
    # 10. Thank you / Q&A
    {
        "layout": "title",
        "title": "Thank You",
        "subtitle": "Questions & Discussion\n\n"
                    "A Comparative Analysis of Classical Machine Learning "
                    "Models for Fake News Detection in the Uzbek Language\n"
                    "Code & thesis: see project repository",
    },
]


if __name__ == "__main__":
    out = "presentation/Defense_Presentation_Uzbek_Fake_News.pptx"
    pptxgen.build_presentation(SLIDES, out)
    print("wrote %s (%d slides)" % (out, len(SLIDES)))
