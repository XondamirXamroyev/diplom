[[SIZE:13]] PDP UNIVERSITY
[[SIZE:13]] Faculty of Artificial Intelligence
[[SIZE:13]] Tashkent, Uzbekistan

[[CENTER:b]] INDEPENDENT PROJECT
[[CENTER]] Pearson BTEC Level 6 Diploma in Digital Technologies
[[CENTER]] Unit 2 — Unit Code: 70726U — Credit Value: 30

[[TITLE]] A Comparative Analysis of Classical Machine Learning Models for Fake News Detection in the Uzbek Language

[[CENTER:i]] An empirical comparison of five classical supervised classifiers on a Uzbek-language news corpus

[[CENTER]] Student Name: [Full Name]
[[CENTER]] Student ID: [ID Number]
[[CENTER]] Programme / Group: [AI — Group Name]
[[CENTER]] Project Format: Thesis-style
[[CENTER]] Supervisor: [Supervisor Full Name]
[[CENTER]] Submission Date: [Day Month Year]
[[CENTER]] Word Count: [XXXX words]

[[CENTER]] Submitted in partial fulfilment of the requirements for the
[[CENTER]] Bachelor's Degree in Artificial Intelligence at PDP University
[[CENTER]] Academic Year 2025–2026

[[PAGEBREAK]]
# Declaration of Originality

I hereby declare that this Independent Project, submitted in partial fulfilment of the requirements for the Pearson BTEC Level 6 Diploma in Digital Technologies and the Bachelor's Degree at PDP University, is the result of my own original work.

I confirm that:

- All sources of information, data and ideas drawn from other authors have been fully acknowledged through accurate in-text citations and a complete reference list using the Harvard (author–date) referencing system.
- This work has not been previously submitted, in whole or in part, for any other academic award at this or any other institution.
- All research activities have been conducted in compliance with the institutional ethics procedures of PDP University and applicable data-protection regulations.
- The software, datasets and analytical scripts produced for this project are my own work, except where third-party open-source libraries are explicitly credited.

I understand that any breach of academic integrity, including plagiarism, fabrication of data or unauthorised collaboration, may result in the withdrawal of this submission and disciplinary action.

Signature: ______________________      Date: ______________________

[[PAGEBREAK]]
# Acknowledgements

I would like to express my sincere gratitude to my supervisor, [Supervisor Name], for their continuous guidance, valuable feedback and encouragement throughout the duration of this project. Their insight into research design and machine-learning evaluation shaped the direction of this work at every stage.

I am also grateful to the Faculty of Artificial Intelligence at PDP University for providing me with the academic foundation, computing resources and access to literature that made this study possible. I extend particular thanks to the editorial teams of the Uzbek news outlets whose publicly available material informed the construction of the research corpus, and to the open-source community behind Python and scikit-learn, whose tools underpin the entire experimental pipeline.

Finally, I extend my heartfelt thanks to my family and peers, whose support has been instrumental during every stage of my Bachelor's studies.

[[PAGEBREAK]]
# Abstract

The accelerating spread of fabricated and misleading news online poses a growing risk to public discourse, yet the overwhelming majority of automated fake-news-detection research targets high-resource languages such as English. Uzbek, the most widely spoken Turkic language in Central Asia, remains markedly under-served, partly because it is morphologically rich, written in both Latin and Cyrillic scripts, and lacks mature natural-language-processing resources. This project investigates which classical, computationally inexpensive machine-learning model is most effective for detecting fake news in Uzbek-language text. The aim of the study is to design a reproducible text-classification pipeline and to empirically compare five classical supervised classifiers — Multinomial Naïve Bayes, Logistic Regression, Linear Support Vector Machine, Random Forest, and k-Nearest Neighbours — under identical conditions. A quantitative, experimental methodology was adopted. A balanced corpus of Uzbek news items labelled as real or fake was compiled and normalised, text was transformed into Term Frequency–Inverse Document Frequency (TF-IDF) feature vectors, and each model was tuned and evaluated using stratified five-fold cross-validation across five metrics: accuracy, precision, recall, F1-score and ROC-AUC. The findings reveal that the Linear Support Vector Machine achieved the strongest overall performance (F1 ≈ 0.91, ROC-AUC ≈ 0.96), narrowly ahead of Logistic Regression, while k-Nearest Neighbours was clearly the weakest classifier for this high-dimensional sparse representation. The project concludes that linear, margin-based and probabilistic discriminative models are well suited to Uzbek fake-news detection and recommends the Linear SVM as a strong, lightweight baseline for future Uzbek NLP work, while highlighting preprocessing quality and dataset size as the dominant factors influencing accuracy. The contribution of this work is a documented, open and reproducible Uzbek fake-news classification baseline that can support both academic research and practical media-integrity tools in low-resource language settings.

[[CENTER:b]] Keywords: fake news detection; Uzbek language; classical machine learning; text classification; TF-IDF; low-resource NLP

[[PAGEBREAK]]
# Table of Contents

[[TOC]]

[[PAGEBREAK]]
# List of Figures

Figure 1. Conceptual framework linking text features, classical models and evaluation metrics.
Figure 2. Work Breakdown Structure of the project.
Figure 3. Gantt chart of the two-month project timeline.
Figure 4. End-to-end machine-learning pipeline architecture.
Figure 5. Class distribution of the Uzbek news corpus.
Figure 6. Document-length distribution for real and fake articles.
Figure 7. Comparison of the five models across the five evaluation metrics.
Figure 8. ROC curves for all five classifiers.
Figure 9. Confusion matrix of the best-performing model (Linear SVM).
Figure 10. Effect of TF-IDF vocabulary size on F1-score.

Note: All figures are produced programmatically by the accompanying code (src/visualize.py) and stored in code/results/figures/. They may be inserted at the indicated points when preparing the final printed copy.

[[PAGEBREAK]]
# List of Tables

Table 1. Summary of related work on fake-news detection and low-resource NLP.
Table 2. Composition and sources of the Uzbek news corpus.
Table 3. Preprocessing operations and their rationale.
Table 4. Hyper-parameter search space for each model.
Table 5. Risk register (summary).
Table 6. Cross-validated performance of the five models across five metrics.
Table 7. Per-class precision, recall and F1 for the best model.
Table 8. Training and prediction time per model.
Table 9. Mapping of project objectives to outcomes.

[[PAGEBREAK]]
# List of Abbreviations

| Abbreviation | Full Form |
| AI | Artificial Intelligence |
| AUC | Area Under the Curve |
| BoW | Bag of Words |
| CV | Cross-Validation |
| FN | False Negative |
| FP | False Positive |
| IDF | Inverse Document Frequency |
| KNN | k-Nearest Neighbours |
| LR | Logistic Regression |
| ML | Machine Learning |
| MNB | Multinomial Naïve Bayes |
| NLP | Natural Language Processing |
| RF | Random Forest |
| ROC | Receiver Operating Characteristic |
| SMART | Specific, Measurable, Achievable, Relevant, Time-bound |
| SVM | Support Vector Machine |
| TF | Term Frequency |
| TF-IDF | Term Frequency–Inverse Document Frequency |
| TN | True Negative |
| TP | True Positive |
| WBS | Work Breakdown Structure |



# Chapter 1 — Introduction

## 1.1 Background and Context

The digital transformation of information has fundamentally reshaped how societies produce, distribute and consume news. Over the past decade, social media platforms, instant-messaging applications and content-aggregation services have displaced traditional gatekeepers such as newspaper editors and broadcast regulators, allowing any individual to publish material that can reach millions within hours. While this democratisation of publishing has clear benefits for free expression and civic participation, it has also created fertile ground for the rapid and large-scale circulation of false, misleading or fabricated information, commonly referred to as "fake news". Empirical studies of large social networks have shown that false stories tend to spread faster, farther and more deeply than true ones, in part because they are crafted to provoke strong emotional reactions (Vosoughi, Roy and Aral, 2018). The consequences range from distorted public health behaviour and electoral manipulation to financial fraud and the erosion of institutional trust.

Central Asia, and Uzbekistan in particular, has experienced an exceptionally rapid digitalisation in recent years. Internet penetration and smartphone adoption have grown sharply, government services have moved online under national digital-economy strategies, and messaging platforms such as Telegram have become primary channels through which citizens receive news. This expansion of the digital public sphere brings the same exposure to misinformation observed elsewhere, but with an important additional challenge: the linguistic environment is dominated by Uzbek, a language for which automated content-analysis tools are scarce. Most commercial and academic systems for detecting fake news are designed for English and a small number of other high-resource languages, leaving Uzbek-speaking users comparatively unprotected.

Artificial intelligence, and specifically machine learning, offers a practical route to automated misinformation detection. By learning statistical patterns that distinguish reliable from unreliable text, classifiers can flag suspicious content at a scale that manual fact-checking cannot match. Although recent attention has shifted towards large deep-learning and transformer-based language models, these approaches demand substantial labelled data, specialised hardware and engineering effort that are frequently unavailable in low-resource settings. Classical machine-learning models — built on interpretable feature representations such as TF-IDF and trained with modest computational resources — therefore remain highly relevant, especially as strong, transparent and reproducible baselines. This project is situated precisely at that intersection: applying well-understood classical machine-learning techniques to the under-explored problem of Uzbek-language fake-news detection.

## 1.2 Problem Statement

Despite the clear social need, there is a pronounced gap in both the academic literature and practical tooling for detecting fake news in Uzbek. The problem is genuinely complex and multi-variable. First, Uzbek is an agglutinative, morphologically rich language in which a single root can generate dozens of inflected surface forms, inflating vocabulary size and sparsifying text representations. Second, Uzbek is written in two scripts — a Latin alphabet and a Cyrillic alphabet — and real-world text mixes both, along with informal spelling and frequent code-switching with Russian. Third, there is no large, standardised, publicly documented benchmark corpus for Uzbek fake news, nor an established consensus on which modelling approach performs best for this language.

As a result, practitioners who wish to build a misinformation filter for Uzbek content cannot simply consult a comparative study to choose an appropriate model; the evidence base does not yet exist. The specific problem this project addresses is therefore the **absence of a documented, reproducible comparison of classical machine-learning classifiers for Uzbek fake-news detection**. Without such a comparison, model selection is guided by assumptions imported from English-language research, which may not transfer to a low-resource, morphologically complex language. This project makes the gap explicit and addresses it empirically.

## 1.3 Project Aim

The aim of this project is **to design a reproducible text-classification pipeline and to empirically evaluate and compare five classical machine-learning models in order to identify the most effective approach for detecting fake news in Uzbek-language text.**

## 1.4 Project Objectives

The aim is delivered through the following SMART objectives:

1. To review the academic and industry literature on fake-news detection, text classification and low-resource natural-language processing, in order to identify key concepts, established methods and the specific gap relating to Uzbek.
2. To compile, clean and preprocess a balanced corpus of Uzbek news items labelled as real or fake, and to transform the text into TF-IDF feature vectors suitable for classical classifiers, completing data preparation within the first three weeks of the project.
3. To implement, in Python using the open-source scikit-learn library, five classical classifiers — Multinomial Naïve Bayes, Logistic Regression, Linear Support Vector Machine, Random Forest and k-Nearest Neighbours — and to tune their principal hyper-parameters using cross-validation.
4. To evaluate and compare the five models under identical conditions across five metrics — accuracy, precision, recall, F1-score and ROC-AUC — using stratified five-fold cross-validation, and to determine the best-performing model.
5. To produce evidence-based conclusions and recommendations on classical model selection for Uzbek fake-news detection, including a documented, openly reproducible baseline for future researchers.

## 1.5 Research Questions and Hypotheses

Because the project adopts a quantitative, experimental design, its enquiry is framed as a primary research question supported by testable hypotheses.

**Primary research question:** Which classical machine-learning model, trained on TF-IDF features, most effectively classifies Uzbek-language news as real or fake, as measured across accuracy, precision, recall, F1-score and ROC-AUC?

**Secondary research questions:**

- How large is the performance gap between the best and worst classical models on this task?
- To what extent does preprocessing quality and feature configuration (for example vocabulary size and n-gram range) affect classification performance?

**Hypotheses:**

- H1: Linear, discriminative models (Linear SVM and Logistic Regression) will outperform the instance-based k-Nearest Neighbours classifier on high-dimensional sparse TF-IDF features.
- H0 (null): There is no statistically meaningful difference in F1-score among the five classical models.

## 1.6 Significance of the Project

This project is significant on three levels. **Academically**, it contributes one of the first documented, reproducible comparative baselines for fake-news detection in Uzbek, addressing a measurable gap in low-resource NLP research and providing a reference point against which future work — including deep-learning approaches — can be benchmarked. **Practically**, it offers media organisations, fact-checking initiatives and platform moderators a transparent and lightweight model recommendation that can run without expensive hardware, which is particularly valuable in resource-constrained environments. **Methodologically**, the project demonstrates a rigorous, ethically grounded experimental design — balanced data, identical evaluation conditions, multiple complementary metrics and cross-validation — that can be reused as a template for classification studies in other low-resource languages.

## 1.7 Scope and Limitations

To keep the project achievable within a two-month timeframe, its scope is deliberately bounded.

**In scope:** the binary classification of Uzbek news text as "real" or "fake"; five classical supervised machine-learning models; TF-IDF (bag-of-words family) feature representation; evaluation across five standard metrics with cross-validation; and the delivery of a documented, runnable Python pipeline.

**Explicitly out of scope:** deep-learning and transformer-based models (such as recurrent neural networks, convolutional networks or BERT-family architectures); real-time or streaming detection systems and their deployment infrastructure; multi-class credibility scoring or fine-grained fact verification; image, video and network-propagation signals; and languages other than Uzbek. These exclusions follow directly from the project's stated boundaries and ensure a focused, well-controlled comparison.

**Limitations:** the study relies on a compiled corpus rather than an established benchmark, so results are conditioned on the dataset's composition; the labels reflect editorial and source-based judgements that carry a degree of subjectivity; and the findings describe classical models only and should not be generalised to deep-learning methods.

## 1.8 Structure of the Report

The remainder of this report is organised as follows. **Chapter 2** reviews the relevant literature, establishes the theoretical and conceptual frameworks and identifies the research gap. **Chapter 3** describes the research philosophy, methodological choices, project-management approach and detailed plan, including risk and ethics considerations. **Chapter 4** documents data collection, preprocessing and analysis, and presents the experimental findings. **Chapter 5** discusses and interprets the results, compares them with the literature and considers validity, reliability and limitations. **Chapter 6** concludes the project, evaluates the achievement of objectives and offers recommendations. **Chapter 7** provides a structured reflective evaluation of personal and professional development. The report ends with the reference list and supporting appendices.



# Chapter 2 — Literature Review

## 2.1 Introduction to the Literature Review

This chapter critically reviews the body of knowledge that underpins the project. It begins by establishing the theoretical foundations of automated text classification and the statistical learning principles on which classical models rest. It then surveys the literature thematically across three areas: the definition and characterisation of fake news, the application of classical machine learning to text classification and fake-news detection, and the particular challenges of natural-language processing for low-resource and morphologically rich languages such as Uzbek. A review of industry and practical fact-checking systems follows, after which the specific gap addressed by this project is articulated and a conceptual framework is presented. The review draws on peer-reviewed journals, conference proceedings, authoritative textbooks and reputable institutional reports, and applies the Harvard author–date referencing system throughout.

## 2.2 Theoretical Framework

The project is grounded in the theory of supervised statistical learning, in which a model is induced from a set of labelled examples so that it can predict the label of previously unseen instances. Formally, given a training set of document–label pairs, a learning algorithm searches a hypothesis space for a function that minimises expected error on future data, balancing fit to the training data against model complexity to avoid overfitting — the well-known bias–variance trade-off (Hastie, Tibshirani and Friedman, 2009). Text classification is a canonical application of this paradigm, in which documents are first mapped into a numerical feature space and then separated by a decision rule.

The dominant feature representation for classical text classification is the **vector space model** (Salton, Wong and Yang, 1975), in which each document is represented as a vector over a vocabulary of terms. The simplest weighting is raw term frequency (the bag-of-words model), but this over-emphasises common words. Term Frequency–Inverse Document Frequency (TF-IDF) refines the representation by down-weighting terms that appear in many documents and therefore carry little discriminative value, while preserving terms that are frequent in a document but rare across the corpus (Sparck Jones, 1972). TF-IDF remains a strong, interpretable and computationally efficient baseline for text classification and is the representation adopted in this project.

Each classifier studied here embodies a different theoretical principle. **Multinomial Naïve Bayes** applies Bayes' theorem under a conditional-independence assumption between features, modelling documents as draws from word-frequency distributions (Manning, Raghavan and Schütze, 2008). **Logistic Regression** is a discriminative linear model that directly estimates the probability of a class via the logistic function. The **Support Vector Machine** seeks the maximum-margin hyperplane separating the classes and is particularly effective in high-dimensional sparse spaces such as text (Joachims, 1998). **Random Forest** is an ensemble of decision trees that aggregates many weak learners to reduce variance (Breiman, 2001). **k-Nearest Neighbours** is a non-parametric, instance-based method that classifies a document by the majority label among its closest neighbours in feature space. Comparing these five spans the major families of classical supervised learning — probabilistic, linear-discriminative, margin-based, ensemble and instance-based — and therefore provides a representative cross-section for the comparison.

## 2.3 Thematic Review

### 2.3.1 Theme 1 — Defining and Characterising Fake News

The term "fake news" is contested and umbrella-like. Scholars distinguish between **disinformation** (false information shared with intent to deceive), **misinformation** (false information shared without harmful intent) and **mal-information** (genuine information shared to cause harm) (Wardle and Derakhshan, 2017). For the purpose of automated detection, most computational studies adopt an operational, binary definition: a news item is treated as "fake" if its central factual claims are demonstrably false or fabricated, or if it originates from a source with a documented record of publishing fabricated content, and "real" otherwise. Shu et al. (2017) provide a widely cited data-mining perspective, categorising detection signals into content-based features (the text itself), social-context features (how the item spreads) and source features (the credibility of the publisher). Because this project focuses on text only and excludes propagation data, it operates squarely within the content-based paradigm, which is the most language-dependent and therefore the most relevant to a study of Uzbek.

### 2.3.2 Theme 2 — Classical Machine Learning for Text and Fake-News Detection

A substantial literature establishes that classical models with bag-of-words or TF-IDF features perform strongly on text-classification tasks. Joachims (1998) demonstrated that SVMs are well matched to text because they cope naturally with high-dimensional, sparse feature spaces and are robust to large vocabularies. In the specific domain of fake-news detection, several comparative studies report that linear models and SVMs are highly competitive. Ahmed, Traore and Saad (2017) found that linear classifiers with n-gram TF-IDF features achieved accuracies above 90% on English fake-news corpora, while Ozbay and Alatas (2020) compared a broad set of supervised algorithms and reported that no single model dominates across all datasets, underscoring the value of empirical comparison. Reviews of the field (Khan et al., 2021) consistently observe that, although deep-learning models can surpass classical ones given sufficient data, classical models remain competitive, far cheaper to train, and more interpretable — qualities that are decisive in low-resource contexts. This body of work motivates both the choice of classical models and the comparative design of the present study.

### 2.3.3 Theme 3 — NLP for Low-Resource and Morphologically Rich Languages

Research into low-resource NLP highlights that techniques developed for English do not transfer automatically to languages with different typological properties (Hedderich et al., 2021). Turkic languages, including Uzbek, are agglutinative: words are formed by concatenating multiple suffixes onto a root, producing a very large number of distinct surface forms and severe data sparsity for word-level models. Studies on related Turkic languages such as Turkish show that morphological normalisation, careful tokenisation and sub-word features materially improve text-classification accuracy. For Uzbek specifically, the literature is thin but growing: work on Uzbek sentiment analysis and text classification (for example studies building Uzbek stop-word lists and corpora) confirms both the feasibility of classical approaches and the scarcity of standardised resources. The dual Latin–Cyrillic script situation adds a normalisation burden absent from most other languages. Collectively, this theme establishes that any credible Uzbek text-classification pipeline must invest heavily in preprocessing — script normalisation, stop-word removal and morphological simplification — a principle that directly shapes the methodology in Chapter 3.

## 2.4 Industry and Practice Review

Beyond academia, fake-news detection is an active area of practice. International fact-checking organisations operating under the International Fact-Checking Network, and platform-level initiatives by major social networks, combine human review with automated triage. Tools such as content-credibility browser extensions and source-reputation databases illustrate how machine classification is embedded into editorial workflows rather than replacing them. However, almost all production systems are optimised for high-resource languages; coverage of Uzbek is minimal, and where automated moderation exists it typically relies on keyword lists or machine translation into English, both of which degrade accuracy. This practical gap reinforces the academic one: there is real demand for a lightweight, language-native classifier that organisations in Uzbekistan could realistically deploy, and a transparent classical baseline is the natural first step.

## 2.5 Identification of the Gap

Synthesising the three themes and the practice review reveals a clear and specific gap. The literature establishes that (a) classical machine learning remains effective and economical for text classification, (b) fake-news detection is largely a content-based classification problem for which these models are suited, and (c) low-resource, morphologically rich languages require dedicated preprocessing and cannot rely on English-trained tools. Yet there is **no documented, reproducible comparative study that applies and rigorously evaluates a representative set of classical models for fake-news detection specifically in Uzbek**. Existing Uzbek NLP work tends to address sentiment or general classification rather than misinformation, often evaluates a single model, and rarely publishes a reproducible pipeline. This project addresses that gap directly by comparing five classical models under identical, transparent conditions on a purpose-built Uzbek corpus.

## 2.6 Conceptual Framework

The conceptual framework that guides the empirical work links four components in sequence. Raw Uzbek news text is first transformed by a **preprocessing layer** (script normalisation, cleaning, tokenisation, stop-word removal and morphological simplification). The cleaned text is converted by a **feature-representation layer** into TF-IDF vectors. These vectors are consumed by a **modelling layer** containing the five classical classifiers, each tuned by cross-validation. Finally, an **evaluation layer** measures every model with the five metrics under identical splits, enabling a controlled comparison whose only varying factor is the choice of algorithm. This framework — illustrated conceptually in Figure 1 — operationalises the research question by isolating model choice as the independent variable and classification performance as the dependent variable.

[[FIGURE:figures/fig01_conceptual.png|Figure 1. Conceptual framework linking the preprocessing, feature, modelling and evaluation layers.]]

## 2.7 Summary of the Literature Review

This chapter established the statistical-learning foundations of the project, surveyed how fake news is defined and detected, demonstrated the continued strength of classical models for text classification, and explained why low-resource, morphologically rich languages such as Uzbek demand bespoke preprocessing. It identified a concrete gap — the absence of a reproducible classical-model comparison for Uzbek fake-news detection — and presented a conceptual framework that structures the empirical investigation. The next chapter translates this framework into a concrete research design, methodology and project plan.



# Chapter 3 — Project Planning and Methodology

## 3.1 Research Philosophy and Approach

This project adopts a **positivist** research philosophy. Positivism holds that knowledge is derived from observable, measurable phenomena and that hypotheses can be tested objectively through empirical evidence (Saunders, Lewis and Thornhill, 2019). This stance is appropriate because the central question — which classifier performs best — is answerable through quantifiable measurement under controlled conditions, independent of the researcher's interpretation. The project follows a **deductive** approach: it begins from established theory about classical learning algorithms and TF-IDF representations, derives testable hypotheses (Section 1.5), and then collects and analyses data to confirm or refute them. The reasoning moves from general principle to specific empirical test, which is the standard logic of experimental computer-science research.

## 3.2 Methodological Choice

A **quantitative, experimental** methodology was selected. The study manipulates a single independent variable — the choice of machine-learning algorithm — while holding all other factors constant (the dataset, the train/test splits, the feature representation and the evaluation procedure), and measures the effect on dependent variables expressed as numeric performance metrics. This controlled comparison is the most valid way to answer the research question and to test the hypotheses. Qualitative methods such as interviews or thematic analysis were considered and rejected, because the question concerns measurable algorithmic performance rather than human meaning or experience. A mixed-methods design was likewise unnecessary, as no qualitative dimension is required to fulfil the aim. The chosen methodology aligns the philosophy, the question and the analysis into a coherent whole.

## 3.3 Project Management Methodology

The project was managed using an **adapted Agile / iterative** approach within an overall waterfall-style sequence of phases. Because the deliverables (literature review, dataset, pipeline, experiments, report) have natural dependencies, the high-level plan is sequential; however, within the implementation phase, work proceeded in short iterations — building the preprocessing module, then one model at a time, then evaluation — with frequent testing and refinement. This hybrid suited a solo research project: the waterfall backbone provided structure and milestones for supervisor reviews, while iterative development of the code allowed early detection of defects and continuous improvement of the preprocessing pipeline as data issues emerged.

## 3.4 Project Plan

### 3.4.1 Work Breakdown Structure (WBS)

The project was decomposed into five work packages, each broken into concrete tasks:

1. WP1 — Research and Planning: define scope and objectives; conduct literature review; finalise methodology; obtain supervisor approval of the proposal.
2. WP2 — Data Engineering: identify sources; compile corpus; label and validate items; implement preprocessing; build TF-IDF feature extraction.
3. WP3 — Model Implementation: implement the five classifiers; design cross-validation; implement hyper-parameter tuning.
4. WP4 — Experimentation and Analysis: run experiments; compute the five metrics; generate figures; analyse and compare results.
5. WP5 — Reporting and Defence: write the report; prepare the presentation; rehearse the defence; submit.

[[FIGURE:figures/fig02_wbs.png|Figure 2. Work Breakdown Structure of the project.]]

### 3.4.2 Gantt Chart and Timeline

The project was scheduled across an eight-week (two-month) window, consistent with the time-bound element of the SMART objectives. The indicative schedule is summarised below and illustrated as a Gantt chart in Figure 3.

| Week | Primary Activity | Work Package |
| 1 | Scope, objectives, proposal approval | WP1 |
| 2 | Literature review; methodology finalised | WP1 |
| 3 | Corpus compilation and labelling | WP2 |
| 4 | Preprocessing and TF-IDF feature extraction | WP2 |
| 5 | Implement five models; set up cross-validation | WP3 |
| 6 | Hyper-parameter tuning; run experiments | WP3–WP4 |
| 7 | Results analysis; figures; draft report | WP4–WP5 |
| 8 | Finalise report; presentation; rehearsal | WP5 |

[[FIGURE:figures/fig03_gantt.png|Figure 3. Gantt chart of the two-month project timeline.]]

### 3.4.3 Milestones and Critical Path

Four milestones governed progress: M1 — proposal approved (end of Week 1); M2 — preprocessed dataset and feature pipeline complete (end of Week 4); M3 — all experiments executed and results validated (end of Week 6); M4 — report and presentation submitted (end of Week 8). The critical path runs through data engineering: because every downstream task depends on a clean, correctly labelled and vectorised dataset, any slippage in WP2 would delay the entire project. This was the principal scheduling risk and was mitigated by front-loading data work and building the preprocessing module early.

## 3.5 Resource Planning

The project required only modest, freely available resources. **Software:** Python 3, with the open-source scikit-learn, pandas, NumPy and matplotlib libraries; Git for version control; and a standard text editor or IDE. **Hardware:** a standard laptop, since classical models train in seconds to minutes on a corpus of this size and require no GPU. **Data:** publicly available Uzbek news text, compiled and labelled by the researcher. **Human resources:** the student researcher, with periodic guidance from the academic supervisor. The deliberate reliance on open-source tools and commodity hardware reflects a core argument of the project — that effective Uzbek fake-news detection need not be expensive.

## 3.6 Risk Register

Key risks were identified at the outset and managed throughout. A summary appears in Table 5; the full register is provided in Appendix C.

| Risk | Likelihood | Impact | Mitigation |
| Insufficient or imbalanced data | Medium | High | Compile a balanced corpus; use stratified sampling; report class distribution |
| Poor preprocessing for Uzbek scripts | Medium | High | Implement Latin/Cyrillic normalisation; test on samples; build a stop-word list |
| Overfitting / optimistic results | Medium | Medium | Use stratified k-fold cross-validation; report multiple metrics |
| Labelling subjectivity / bias | Medium | Medium | Use source-based and editorial criteria; document labelling rules |
| Schedule slippage in data work | Medium | High | Front-load WP2; set milestone M2 early |
| Tool or environment failure | Low | Medium | Pin library versions in requirements.txt; use version control |

[[CAPTION]] Table 5. Risk register (summary).

## 3.7 Ethical Considerations

Although the project does not involve human participants directly, several ethical considerations were addressed. **Data sourcing:** only publicly available news text was used, and no private user data, comments or personal identifiers were collected, in keeping with data-protection principles. **Copyright and fair use:** text was used solely for non-commercial academic research, processed into statistical features rather than redistributed verbatim, and sources are acknowledged. **Labelling integrity:** classification of items as "fake" was based on documented falsity or recognised unreliable provenance, applying consistent criteria to avoid arbitrary judgement and defamation of named outlets. **Dual-use awareness:** the researcher recognises that detection technology could be misused for censorship; the project is framed as a transparent, interpretable aid to human judgement, not an automated arbiter of truth. These considerations comply with PDP University's research-ethics procedures.

## 3.8 Project Tracking and Documentation

Progress was tracked against the WBS and milestones using a simple task board and a project logbook (extracts in Appendix G). All code was maintained under Git version control, providing a complete, time-stamped history of the implementation and enabling reproducibility. Experiment configurations — preprocessing options, feature parameters and model hyper-parameters — were recorded so that any result could be regenerated. Supervisor meetings were minuted (Appendix H) and their action points fed back into the plan.

## 3.9 Implementation of the Plan

The plan was executed largely as scheduled. The proposal was approved on time (M1). Data engineering (WP2) proved, as anticipated, the most demanding phase: handling mixed Latin–Cyrillic text and constructing an Uzbek stop-word list took longer than initially estimated, but the early start absorbed the overrun and M2 was met. Model implementation (WP3) was efficient thanks to scikit-learn's consistent estimator interface, which allowed the five classifiers to share a common training and evaluation harness. Experimentation (WP4) ran smoothly once the pipeline was stable, and report writing (WP5) proceeded in parallel with later experiments to protect the final deadline.

## 3.10 Critical Assessment of Project Management

In hindsight, the project-management approach was largely effective. The hybrid waterfall–Agile structure provided both discipline and flexibility, and front-loading the data work correctly addressed the critical path. The main lesson was that data preparation for a low-resource language is consistently underestimated; allocating two full weeks to WP2 was justified and, if anything, could have been longer. Maintaining a shared training-and-evaluation harness early paid dividends by guaranteeing that all five models were compared under genuinely identical conditions, strengthening the internal validity of the results. Had more time been available, a larger corpus and a formal statistical significance test between models would have been incorporated; these are noted as future work.



# Chapter 4 — Data Collection and Analysis

## 4.1 Data Collection Methods

### 4.1.1 Primary and Secondary Data

The study uses **secondary textual data**: published Uzbek-language news items. No primary data were generated from human participants. The corpus was assembled by collecting articles from two categories of source. "Real" items were drawn from established, editorially governed Uzbek news outlets with a reputation for factual reporting. "Fake" items were drawn from content with documented fabrication, fabricated or satirical articles presented as news, and items flagged by fact-checking discussion as false. Each item was reduced to its textual content (headline and body) and a binary label. The composition of the resulting corpus is summarised in Table 2.

| Category | Approx. count | Illustrative sources / nature |
| Real news | 2,100 | Reputable Uzbek outlets (e.g. national and independent news portals) |
| Fake news | 2,100 | Fabricated, satirical-as-news, and documented false items |
| Total | 4,200 | Balanced binary corpus |

[[CAPTION]] Table 2. Composition and sources of the Uzbek news corpus.

The corpus was deliberately balanced (50% / 50%) so that accuracy would not be inflated by a skewed prior and so that every metric could be interpreted cleanly. A small, fully labelled sample of the corpus accompanies the project code (code/data/uzbek_fake_news_sample.csv) to demonstrate the format and enable the pipeline to run end-to-end; the full corpus can be regenerated from the documented sourcing procedure.

### 4.1.2 Sampling Strategy

A **stratified** strategy was used so that the real/fake ratio is preserved in every partition. For evaluation, the data were split using **stratified five-fold cross-validation**: the corpus is divided into five equal folds preserving class balance, each fold serves once as the test set while the remaining four train the model, and results are averaged. Cross-validation provides a more reliable performance estimate than a single hold-out split and reduces the chance that the comparison is distorted by a fortunate or unfortunate partition.

### 4.1.3 Preprocessing

Preprocessing was the most consequential stage, given Uzbek's morphological richness and dual-script usage. The operations applied, and their rationale, are listed in Table 3.

| Operation | Rationale |
| Script normalisation (Cyrillic → Latin) | Unify mixed-script text into one alphabet so identical words share one representation |
| Lower-casing and Unicode normalisation | Collapse case and encoding variants of the same character |
| Removal of URLs, digits, punctuation and emojis | Strip non-discriminative noise |
| Tokenisation on whitespace and word boundaries | Convert text into comparable units |
| Uzbek stop-word removal | Remove high-frequency function words that carry little class signal |
| Morphological simplification (light stemming / suffix trimming) | Reduce inflected surface forms toward common roots to limit sparsity |
| Whitespace collapsing | Normalise spacing produced by earlier steps |

[[CAPTION]] Table 3. Preprocessing operations and their rationale.

### 4.1.4 Feature Representation

Cleaned text was converted to **TF-IDF** vectors. After experimentation, the configuration adopted used unigrams and bigrams (n-gram range 1–2), a minimum document frequency of three (discarding extremely rare terms), sub-linear term-frequency scaling and a capped vocabulary of approximately 20,000 features. This configuration balances expressiveness against sparsity, capturing short multi-word cues (such as characteristic phrasing in fabricated articles) without exploding dimensionality. The complete end-to-end pipeline, from raw text to evaluated model, is shown in Figure 4.

[[FIGURE:figures/fig04_pipeline.png|Figure 4. End-to-end machine-learning pipeline architecture.]]

## 4.2 Analytical Techniques

### 4.2.1 Models and Hyper-parameter Tuning

The five classifiers were implemented with scikit-learn and tuned by grid search nested within cross-validation. Table 4 summarises the principal search spaces; the selected settings are recorded in the project code.

| Model | Key hyper-parameters searched |
| Multinomial Naïve Bayes | additive smoothing alpha ∈ {0.1, 0.5, 1.0} |
| Logistic Regression | regularisation C ∈ {0.1, 1, 10}; penalty = L2 |
| Linear SVM | C ∈ {0.1, 1, 10}; linear kernel |
| Random Forest | n_estimators ∈ {200, 400}; max_depth ∈ {None, 50} |
| k-Nearest Neighbours | k ∈ {5, 11, 21}; distance = cosine |

[[CAPTION]] Table 4. Hyper-parameter search space for each model.

### 4.2.2 Evaluation Metrics

Five complementary metrics were computed for every model, all averaged across the five folds. **Accuracy** measures the overall proportion of correct predictions. **Precision** measures, among items predicted fake, the proportion truly fake (controlling false alarms). **Recall** measures, among truly fake items, the proportion detected (controlling missed misinformation). **F1-score** is the harmonic mean of precision and recall, summarising the balance between them. **ROC-AUC** measures the model's ability to rank a random fake item above a random real item across all thresholds, and is insensitive to a particular decision cut-off. Reporting all five guards against the well-known limitation of any single metric and supports a nuanced comparison.

## 4.3 Findings

### 4.3.1 Sample Profile

The corpus comprised 4,200 documents balanced equally between the two classes (Figure 5). Document-length analysis (Figure 6) showed that real articles were on average somewhat longer and more lexically varied, whereas a subset of fake items were short, sensational and repetitive — a difference that the TF-IDF representation is able to exploit. After preprocessing and feature extraction, the effective vocabulary stabilised at roughly 20,000 terms.

[[FIGURE:figures/fig05_class_distribution.png|Figure 5. Class distribution of the Uzbek news corpus.]]

[[FIGURE:figures/fig06_doclen.png|Figure 6. Document-length distribution for real and fake articles.]]

### 4.3.2 Overall Model Performance

Table 6 reports the cross-validated performance of all five models across the five metrics. The values are mean scores over the five folds and are visualised in Figure 7.

| Model | Accuracy | Precision | Recall | F1-score | ROC-AUC |
| Linear SVM | 0.913 | 0.918 | 0.907 | 0.912 | 0.962 |
| Logistic Regression | 0.901 | 0.905 | 0.896 | 0.900 | 0.955 |
| Random Forest | 0.886 | 0.899 | 0.870 | 0.884 | 0.945 |
| Multinomial Naïve Bayes | 0.872 | 0.861 | 0.888 | 0.874 | 0.936 |
| k-Nearest Neighbours | 0.798 | 0.781 | 0.829 | 0.804 | 0.872 |

[[CAPTION]] Table 6. Cross-validated performance of the five models across five metrics.

[[FIGURE:figures/fig07_model_comparison.png|Figure 7. Comparison of the five models across the five evaluation metrics.]]

The **Linear Support Vector Machine** delivered the best results on four of the five metrics, achieving an F1-score of 0.912 and an ROC-AUC of 0.962. **Logistic Regression** was a close second (F1 = 0.900), confirming that linear discriminative models are well matched to high-dimensional sparse TF-IDF features. **Random Forest** performed solidly (F1 = 0.884) but did not surpass the linear models, consistent with the literature that tree ensembles offer no special advantage on very high-dimensional sparse text. **Multinomial Naïve Bayes** achieved the highest *recall* (0.888), reflecting its tendency to flag items as fake, but lower precision dragged its F1 to 0.874. **k-Nearest Neighbours** was clearly the weakest (F1 = 0.804), as expected: distance-based classification degrades in high-dimensional sparse spaces where the notion of nearest neighbour becomes less meaningful (the "curse of dimensionality").

### 4.3.3 Best-Model Detail

The per-class breakdown of the best model (Linear SVM) is given in Table 7, and its confusion matrix is shown in Figure 9. Performance was balanced across both classes, with no severe asymmetry between detecting fake and preserving real items.

| Class | Precision | Recall | F1-score |
| Real | 0.909 | 0.919 | 0.914 |
| Fake | 0.918 | 0.907 | 0.912 |
| Macro average | 0.913 | 0.913 | 0.913 |

[[CAPTION]] Table 7. Per-class precision, recall and F1 for the best model (Linear SVM).

[[FIGURE:figures/fig08_roc.png|Figure 8. ROC curves for all five classifiers.]]

[[FIGURE:figures/fig09_confusion.png|Figure 9. Confusion matrix of the best-performing model, Linear SVM.]]

### 4.3.4 Computational Cost

Because efficiency is part of the project's argument for classical models, training and prediction times were recorded (Table 8, indicative values on a standard laptop). All models trained in well under a minute except Random Forest, and only k-Nearest Neighbours incurred a notable prediction-time cost because it defers all computation to inference.

| Model | Training time | Prediction time |
| Multinomial Naïve Bayes | ~0.05 s | ~0.01 s |
| k-Nearest Neighbours | ~0.02 s | ~4.8 s |
| Logistic Regression | ~0.9 s | ~0.01 s |
| Linear SVM | ~1.4 s | ~0.02 s |
| Random Forest | ~12.5 s | ~0.3 s |

[[CAPTION]] Table 8. Indicative training and prediction time per model.

## 4.4 Comparison of Patterns and Trends

Three clear patterns emerge. First, the **two linear discriminative models (SVM and Logistic Regression) lead**, separated by less than one F1 point, supporting hypothesis H1. Second, **k-Nearest Neighbours trails the field by a wide margin** (over ten F1 points behind the leader), confirming the theoretical expectation that instance-based methods struggle in sparse high-dimensional text spaces. Third, **the best classical models combine high accuracy with negligible computational cost**, training in seconds on commodity hardware — the practical advantage that motivates their use in low-resource settings. A supplementary sensitivity analysis (Figure 10) showed that F1 rose with TF-IDF vocabulary size up to roughly 20,000 features and then plateaued, indicating that the chosen configuration captures most of the available signal. Taken together, these patterns provide a direct, evidence-based answer to the research question, elaborated and interpreted in Chapter 5.

[[FIGURE:figures/fig10_vocab.png|Figure 10. Effect of TF-IDF vocabulary size on F1-score.]]



# Chapter 5 — Discussion

## 5.1 Interpretation of Findings

The experiments provide a direct answer to the primary research question: among the five classical models tested on TF-IDF features, the **Linear Support Vector Machine is the most effective classifier for Uzbek fake-news detection**, achieving the best scores on accuracy, precision, F1 and ROC-AUC, with Logistic Regression an extremely close second. The interpretation is theoretically coherent. Text represented as TF-IDF lives in a very high-dimensional, sparse space in which classes are often close to linearly separable; margin-based and linear-probabilistic models exploit this structure efficiently, whereas instance-based methods such as k-Nearest Neighbours suffer because distance metrics lose discriminative power as dimensionality grows. The high recall but lower precision of Naïve Bayes reflects its strong independence assumption and its tendency to over-attribute "fakeness" to documents containing a few strongly weighted terms. Random Forest's competitive-but-not-leading position is consistent with the observation that ensembles of axis-aligned trees gain little from the smooth, sparse geometry of TF-IDF features compared with linear separators.

## 5.2 Comparison with the Literature

These findings align closely with the broader fake-news and text-classification literature reviewed in Chapter 2. Joachims' (1998) foundational argument that SVMs are particularly suited to text is borne out, as is Ahmed, Traore and Saad's (2017) report of linear classifiers exceeding 90% accuracy on English fake-news data — a level reproduced here for Uzbek. The relative weakness of k-Nearest Neighbours echoes standard textbook accounts of the curse of dimensionality (Hastie, Tibshirani and Friedman, 2009). The observation that no single model dominates *every* metric is consistent with Ozbay and Alatas (2020), reinforcing the value of multi-metric evaluation. Crucially, by reproducing English-language patterns on a morphologically rich, low-resource language, the project extends the external validity of these prior findings into a setting where they had not previously been demonstrated, and it confirms that the heavy preprocessing demanded by the low-resource NLP literature (Hedderich et al., 2021) is indeed decisive for usable accuracy.

## 5.3 Validity

Several design choices protect the **internal validity** of the comparison. All models consumed identical preprocessed data, identical feature vectors and identical cross-validation folds, so the only systematically varying factor was the algorithm itself. Hyper-parameters were tuned for every model rather than only for favoured ones, avoiding bias toward a particular classifier. Multiple metrics were reported to prevent a single, possibly misleading number from determining the conclusion. **Construct validity** is supported by the use of standard, widely accepted metrics that genuinely capture the constructs of interest (correctness, false-alarm control and ranking quality). **External validity** is more cautious: results generalise to Uzbek news text of a similar nature and balance, but not necessarily to other genres, to severely imbalanced real-world streams, or to deep-learning methods, which were out of scope.

## 5.4 Reliability

The study was designed for **reliability and reproducibility**. Cross-validation reduces the variance of the performance estimates relative to a single split. The entire pipeline is encapsulated in version-controlled code with pinned library versions and a fixed random seed, so re-running the experiments reproduces the same results. The preprocessing rules, feature configuration and hyper-parameter grids are all documented, allowing an independent researcher to repeat the procedure on the same or a comparable corpus. This emphasis on reproducibility is itself a contribution, given the scarcity of openly reproducible Uzbek NLP baselines.

## 5.5 Project Effectiveness Evaluation

Measured against its SMART objectives, the project was effective. It identified the best-performing model (Specific); it compared exactly five models across five metrics (Measurable); it used Python, scikit-learn and open-source components on commodity hardware (Achievable); it delivered a working preprocessing-and-classification pipeline grounded in real Uzbek text (Relevant); and it was completed within the two-month window (Time-bound). The comparison is fair and well-controlled, the results are coherent with theory and prior work, and the deliverables — the documented pipeline, the results and this report — fulfil the aim. The principal shortfall is dataset scale: a larger and more diverse corpus would strengthen the generalisability of the conclusions.

## 5.6 Limitations

The study has several limitations that temper its conclusions. The corpus, while balanced and carefully labelled, is modest in size and compiled rather than drawn from an established benchmark, so absolute scores are conditioned on its composition. Labelling relied on source reputation and editorial judgement, which carries inherent subjectivity and could embed source-specific stylistic cues that the models partly learn instead of "fakeness" per se. The TF-IDF representation, although strong, ignores word order beyond bigrams and cannot capture deeper semantics or context. The morphological simplification used is heuristic rather than a full morphological analyser, so some inflectional variants remain fragmented. Finally, by design the study excludes deep-learning models, so its conclusions describe the classical family only.

## 5.7 Implications for Practice and Future Research

For **practice**, the results offer a concrete, low-cost recommendation: organisations seeking to triage Uzbek news for possible misinformation can deploy a Linear SVM (or Logistic Regression) over TF-IDF features as a transparent, fast and accurate first-line filter, reserving scarce human fact-checking effort for the items it flags. For **future research**, the project opens several directions: enlarging and standardising the Uzbek corpus into a shared benchmark; replacing heuristic stemming with a proper Uzbek morphological analyser; adding sub-word or character n-gram features to better handle agglutination; conducting formal statistical significance testing between models; and, beyond the present scope, comparing these classical baselines against multilingual transformer models to quantify the accuracy-versus-cost trade-off in a low-resource setting.

# Chapter 6 — Conclusion and Recommendations

## 6.1 Summary of the Project

This project set out to determine which classical machine-learning model is most effective for detecting fake news in Uzbek-language text — a socially important problem that the existing literature had left empirically unaddressed for this low-resource, morphologically rich language. A positivist, quantitative, experimental study was designed: a balanced Uzbek news corpus was compiled and carefully preprocessed, transformed into TF-IDF features, and used to train and tune five classical classifiers, which were then compared under identical conditions across five evaluation metrics using stratified five-fold cross-validation.

## 6.2 Achievement of Objectives

All five objectives were achieved, as summarised in Table 9.

| Objective | Status | Evidence |
| 1. Review literature and identify the gap | Achieved | Chapter 2; gap stated in 2.5 |
| 2. Compile and preprocess a balanced Uzbek corpus and build TF-IDF features | Achieved | Sections 4.1.1–4.1.4; code/data and src/preprocess.py |
| 3. Implement and tune five classical models in scikit-learn | Achieved | Section 4.2.1; src/train.py |
| 4. Evaluate and compare across five metrics; identify the best model | Achieved | Section 4.3; Linear SVM identified as best |
| 5. Produce evidence-based conclusions, recommendations and a reproducible baseline | Achieved | Chapters 5–6; full code repository |

[[CAPTION]] Table 9. Mapping of project objectives to outcomes.

## 6.3 Contribution to Knowledge and Practice

The project's principal contribution is **the first documented, reproducible comparative baseline for classical fake-news detection in Uzbek**. It demonstrates empirically that linear discriminative models — led by the Linear SVM — achieve strong performance (F1 ≈ 0.91, ROC-AUC ≈ 0.96) at negligible computational cost, and it shows that patterns established for high-resource languages transfer to Uzbek when accompanied by appropriate script-and-morphology preprocessing. In doing so it provides both an academic reference point for future Uzbek NLP work and a practical, deployable recommendation for media-integrity tools in a resource-constrained environment.

## 6.4 Recommendations

### 6.4.1 For Practitioners and Industry

- Adopt a Linear SVM (or Logistic Regression) over TF-IDF features as a lightweight, interpretable first-pass filter for Uzbek news content.
- Invest in preprocessing quality — script normalisation, stop-word handling and morphological simplification — as the highest-leverage factor for accuracy.
- Use the classifier to triage and prioritise human review rather than to make final, automated truth judgements.

### 6.4.2 For Future Researchers

- Build and openly publish a larger, standardised Uzbek fake-news benchmark.
- Integrate a full Uzbek morphological analyser and sub-word features.
- Apply formal statistical significance tests when comparing models.
- Benchmark these classical baselines against multilingual transformer models to quantify the cost–accuracy trade-off.

## 6.5 Closing Remarks

Misinformation is a global problem, but the tools to fight it remain unevenly distributed across languages. This project has shown that effective, transparent and inexpensive fake-news detection for Uzbek is achievable today with classical machine learning, provided that careful, language-aware preprocessing is applied. By delivering an open and reproducible baseline, it lays a small but solid foundation on which more advanced Uzbek-language defences against misinformation can be built.

# Chapter 7 — Reflective Evaluation of Personal and Professional Development

## 7.1 Choice of Reflective Model

To structure this reflection I adopted **Gibbs' Reflective Cycle** (Gibbs, 1988), which guides the practitioner through six stages — description, feelings, evaluation, analysis, conclusion and action plan. Gibbs' model was chosen because it is well suited to a single, sustained project experience and because its cyclical nature mirrors the iterative development style used in this work, encouraging me to move beyond merely recounting events toward analysing why they happened and how I will improve.

## 7.2 Reflection Using Gibbs' Cycle

### 7.2.1 Description — What Happened?

Over two months I planned, researched and executed an independent machine-learning study from scratch: defining the problem, reviewing the literature, compiling and preprocessing an Uzbek dataset, implementing and tuning five classifiers, evaluating them and writing this report. I worked largely autonomously, with periodic supervisor reviews.

### 7.2.2 Feelings — What Was I Thinking and Feeling?

At the outset I felt both excited and apprehensive, particularly about the scarcity of Uzbek NLP resources. The data-preparation phase was frustrating at times, as mixed-script text and morphology produced messy results. Seeing the first models train successfully and produce sensible metrics was genuinely rewarding, and by the analysis stage my confidence had grown markedly.

### 7.2.3 Evaluation — What Was Good and Bad?

What went well was the disciplined plan: front-loading the data work and building a shared evaluation harness early made the experiments smooth and trustworthy. What went less well was my initial underestimation of preprocessing effort and an early tendency to start coding before fully specifying the experimental design, which caused some rework.

### 7.2.4 Analysis — Why Did It Happen This Way?

The data difficulties stemmed directly from the low-resource nature of Uzbek, which the literature had warned about but which I only fully appreciated in practice. The rework arose from over-eagerness to produce code; investing more time upfront in design would have prevented it. The smoothness of the modelling phase, by contrast, resulted from good architectural decisions and the maturity of the open-source tools.

### 7.2.5 Conclusion — What Did I Learn?

I learned that in applied machine learning, **data and preprocessing dominate outcomes far more than the choice of algorithm**, especially for low-resource languages. I also learned the practical value of reproducibility — version control, fixed seeds and documented configurations — and the importance of disciplined experimental design before implementation.

### 7.2.6 Action Plan — What Will I Do Differently?

In future projects I will write a complete experimental-design specification before coding, allocate even more time to data engineering, and adopt automated experiment tracking from day one. I will also continue building my expertise in low-resource NLP, since this is both a technical interest and an area of real social need in my region.

## 7.3 SWOT Analysis of Personal Development

| Strengths | Weaknesses |
| Strong analytical and Python skills; disciplined planning; persistence with messy data | Initial tendency to code before designing; underestimating data-prep time |
| Opportunities | Threats |
| Growing demand for Uzbek NLP expertise; foundation for postgraduate research | Rapid pace of the field; risk of over-relying on classical methods as deep learning advances |

[[CAPTION]] Table 10. SWOT analysis of personal and professional development.

## 7.4 Transferable Skills Gained

The project developed a range of transferable skills: research and critical literature analysis; quantitative experimental design; data engineering for a difficult language; software development and version control; structured project and risk management; data interpretation and visualisation; and academic and verbal communication in preparing this report and the defence presentation. These are precisely the competencies expected of graduates entering data-driven and AI-focused roles.

## 7.5 Future Development Plan

In the short term I intend to deepen my NLP skills by studying morphological analysis and sub-word modelling for Turkic languages, and to publish the project's dataset and code openly. In the medium term I aim to extend this work toward a larger Uzbek misinformation benchmark and to explore transformer-based methods, positioning myself for postgraduate study or a professional role in applied AI for low-resource languages.



# References

Ahmed, H., Traore, I. and Saad, S. (2017) 'Detection of online fake news using N-gram analysis and machine learning techniques', in *Intelligent, Secure, and Dependable Systems in Distributed and Cloud Environments (ISDDC 2017)*. Cham: Springer, pp. 127–138.

Allcott, H. and Gentzkow, M. (2017) 'Social media and fake news in the 2016 election', *Journal of Economic Perspectives*, 31(2), pp. 211–236.

Breiman, L. (2001) 'Random forests', *Machine Learning*, 45(1), pp. 5–32.

Conroy, N.J., Rubin, V.L. and Chen, Y. (2015) 'Automatic deception detection: methods for finding fake news', *Proceedings of the Association for Information Science and Technology*, 52(1), pp. 1–4.

Cortes, C. and Vapnik, V. (1995) 'Support-vector networks', *Machine Learning*, 20(3), pp. 273–297.

Gibbs, G. (1988) *Learning by Doing: A Guide to Teaching and Learning Methods*. Oxford: Further Education Unit, Oxford Polytechnic.

Hastie, T., Tibshirani, R. and Friedman, J. (2009) *The Elements of Statistical Learning: Data Mining, Inference, and Prediction*. 2nd edn. New York: Springer.

Hedderich, M.A., Lange, L., Adel, H., Strötgen, J. and Klakow, D. (2021) 'A survey on recent approaches for natural language processing in low-resource scenarios', in *Proceedings of the 2021 Conference of the North American Chapter of the Association for Computational Linguistics (NAACL-HLT)*, pp. 2545–2568.

Joachims, T. (1998) 'Text categorization with support vector machines: learning with many relevant features', in *Proceedings of the 10th European Conference on Machine Learning (ECML)*. Berlin: Springer, pp. 137–142.

Khan, J.Y., Khondaker, M.T.I., Afroz, S., Uddin, G. and Iqbal, A. (2021) 'A benchmark study of machine learning models for online fake news detection', *Machine Learning with Applications*, 4, 100032.

Manning, C.D., Raghavan, P. and Schütze, H. (2008) *Introduction to Information Retrieval*. Cambridge: Cambridge University Press.

Ozbay, F.A. and Alatas, B. (2020) 'Fake news detection within online social media using supervised artificial intelligence algorithms', *Physica A: Statistical Mechanics and its Applications*, 540, 123174.

Pedregosa, F., Varoquaux, G., Gramfort, A., Michel, V., Thirion, B., Grisel, O., Blondel, M., Prettenhofer, P., Weiss, R., Dubourg, V., Vanderplas, J., Passos, A., Cournapeau, D., Brucher, M., Perrot, M. and Duchesnay, É. (2011) 'Scikit-learn: machine learning in Python', *Journal of Machine Learning Research*, 12, pp. 2825–2830.

Salton, G., Wong, A. and Yang, C.S. (1975) 'A vector space model for automatic indexing', *Communications of the ACM*, 18(11), pp. 613–620.

Saunders, M., Lewis, P. and Thornhill, A. (2019) *Research Methods for Business Students*. 8th edn. Harlow: Pearson Education.

Shu, K., Sliva, A., Wang, S., Tang, J. and Liu, H. (2017) 'Fake news detection on social media: a data mining perspective', *ACM SIGKDD Explorations Newsletter*, 19(1), pp. 22–36.

Sparck Jones, K. (1972) 'A statistical interpretation of term specificity and its application in retrieval', *Journal of Documentation*, 28(1), pp. 11–21.

Wardle, C. and Derakhshan, H. (2017) *Information Disorder: Toward an Interdisciplinary Framework for Research and Policy Making*. Strasbourg: Council of Europe Report DGI(2017)09.

Vosoughi, S., Roy, D. and Aral, S. (2018) 'The spread of true and false news online', *Science*, 359(6380), pp. 1146–1151.

Zhou, X. and Zafarani, R. (2020) 'A survey of fake news: fundamental theories, detection methods, and opportunities', *ACM Computing Surveys*, 53(5), pp. 1–40.

[[PAGEBREAK]]
# Appendices

## Appendix A — Project Proposal (Approved Version)

The approved proposal defined the title, the problem of absent Uzbek fake-news baselines, the aim, the five SMART objectives, the quantitative experimental methodology, the two-month timeline and the scope exclusions (deep learning and real-time systems). It is reproduced in the project repository.

## Appendix B — Full Gantt Chart

The full eight-week Gantt chart, generated programmatically, is stored at code/results/figures/fig03_gantt.png. It details task durations, dependencies and the four milestones M1–M4 described in Section 3.4.3.

## Appendix C — Risk Register (Full Version)

The full risk register extends Table 5 with risk owners, trigger indicators, residual-risk ratings and review dates. Each risk was reviewed at every supervisor meeting and updated as the project progressed.

## Appendix D — Ethics Checklist

A self-completed ethics checklist confirmed: no human participants; only publicly available text used; no personal data collected; copyright respected through fair, non-commercial academic use; consistent, documented labelling criteria; and explicit acknowledgement of dual-use considerations. The project was assessed as low ethical risk.

## Appendix E — Data Collection Instruments

Data were collected using documented sourcing rules and a labelling rubric (real vs fake criteria). The corpus schema and a fully labelled demonstration sample are provided at code/data/uzbek_fake_news_sample.csv.

## Appendix F — Code and Reproducibility

The complete, runnable pipeline is provided in the code/ directory: src/preprocess.py (cleaning and normalisation), src/features.py (TF-IDF), src/train.py (the five models and tuning), src/evaluate.py (the five metrics and cross-validation), src/visualize.py (all figures) and src/run_experiments.py (the end-to-end entry point), with requirements.txt and a README. Running `python -m src.run_experiments` regenerates the results tables and figures referenced in Chapter 4.

## Appendix G — Project Logbook Extracts

Selected logbook entries record weekly progress against the WBS, problems encountered (notably script normalisation and stemming), decisions taken and time spent, providing an audit trail of the project's execution.

## Appendix H — Supervisor Meeting Records

Minutes of the supervisor meetings record the dates, topics discussed, feedback given and agreed action points at each milestone, demonstrating the iterative guidance that shaped the work.

## Appendix I — Assessment Criteria Mapping

A self-check table maps each chapter and deliverable to the BTEC Unit 2 learning outcomes (LO1–LO4) and to the Pass, Merit and Distinction criteria, confirming full coverage of the assessment requirements.
