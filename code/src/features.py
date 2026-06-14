"""
TF-IDF feature extraction.

Configuration (see thesis Section 4.1.4):
  * n-gram range : (1, 2)  unigrams + bigrams
  * min_df       : 3       discard extremely rare terms
  * max_features : 20000   cap vocabulary size
  * sublinear_tf : True    1 + log(tf) scaling

Requires scikit-learn (install via requirements.txt).
"""

from sklearn.feature_extraction.text import TfidfVectorizer


def build_vectorizer(max_features=20000, ngram_range=(1, 2), min_df=3,
                     sublinear_tf=True):
    return TfidfVectorizer(
        max_features=max_features,
        ngram_range=ngram_range,
        min_df=min_df,
        sublinear_tf=sublinear_tf,
        lowercase=False,          # text is already preprocessed
        token_pattern=r"(?u)\b\w+\b",
    )
