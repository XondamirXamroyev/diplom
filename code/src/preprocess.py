"""
Text preprocessing for Uzbek news.

Pipeline stages (see thesis Section 4.1.3):
  1. Cyrillic -> Latin transliteration (unify dual-script text)
  2. lower-casing + Unicode normalisation
  3. removal of URLs, digits, punctuation, emojis
  4. tokenisation
  5. Uzbek stop-word removal
  6. light morphological simplification (suffix trimming)
  7. whitespace collapsing

The functions are dependency-free (pure standard library) so preprocessing can
be tested even without scikit-learn installed.
"""

import re
import unicodedata

from .uzbek_stopwords import UZBEK_STOPWORDS

# ---------------------------------------------------------------------------
# 1. Cyrillic -> Latin transliteration (Uzbek)
# ---------------------------------------------------------------------------
# Order matters: multi-character sequences first.
_CYR_TO_LAT = [
    (" shch", "shch"),
    ("Ш", "sh"), ("ш", "sh"), ("Ч", "ch"), ("ч", "ch"),
    ("Ё", "yo"), ("ё", "yo"), ("Ю", "yu"), ("ю", "yu"),
    ("Я", "ya"), ("я", "ya"), ("Ж", "j"), ("ж", "j"),
    ("Ц", "ts"), ("ц", "ts"), ("Қ", "q"), ("қ", "q"),
    ("Ғ", "gʻ"), ("ғ", "gʻ"), ("Ҳ", "h"), ("ҳ", "h"),
    ("Ў", "oʻ"), ("ў", "oʻ"), ("Й", "y"), ("й", "y"),
    ("А", "a"), ("а", "a"), ("Б", "b"), ("б", "b"),
    ("В", "v"), ("в", "v"), ("Г", "g"), ("г", "g"),
    ("Д", "d"), ("д", "d"), ("Е", "e"), ("е", "e"),
    ("З", "z"), ("з", "z"), ("И", "i"), ("и", "i"),
    ("К", "k"), ("к", "k"), ("Л", "l"), ("л", "l"),
    ("М", "m"), ("м", "m"), ("Н", "n"), ("н", "n"),
    ("О", "o"), ("о", "o"), ("П", "p"), ("п", "p"),
    ("Р", "r"), ("р", "r"), ("С", "s"), ("с", "s"),
    ("Т", "t"), ("т", "t"), ("У", "u"), ("у", "u"),
    ("Ф", "f"), ("ф", "f"), ("Х", "x"), ("х", "x"),
    ("Ъ", "ʼ"), ("ъ", "ʼ"), ("Ь", ""), ("ь", ""),
    ("Э", "e"), ("э", "e"),
]


def cyrillic_to_latin(text):
    for cyr, lat in _CYR_TO_LAT:
        text = text.replace(cyr, lat)
    return text


# ---------------------------------------------------------------------------
# 2-3. Cleaning
# ---------------------------------------------------------------------------
_URL_RE = re.compile(r"https?://\S+|www\.\S+")
_NONWORD_RE = re.compile(r"[^a-zʻʼ\s]")          # keep latin letters + apostrophes
_MULTISPACE_RE = re.compile(r"\s+")


def normalise_apostrophes(text):
    # unify the various apostrophe glyphs used for oʻ, gʻ, and the tutuq belgisi
    for ch in ["`", "´", "'", "ʼ", "ʻ", "‘", "’", "ʿ"]:
        text = text.replace(ch, "ʻ")
    return text


def clean_text(text):
    if text is None:
        return ""
    text = unicodedata.normalize("NFKC", str(text))
    text = cyrillic_to_latin(text)
    text = normalise_apostrophes(text)
    text = text.lower()
    text = _URL_RE.sub(" ", text)
    text = _NONWORD_RE.sub(" ", text)        # drop digits, punctuation, emojis
    text = _MULTISPACE_RE.sub(" ", text).strip()
    return text


# ---------------------------------------------------------------------------
# 4. Tokenisation
# ---------------------------------------------------------------------------
def tokenize(text):
    return [t for t in text.split(" ") if t]


# ---------------------------------------------------------------------------
# 6. Light morphological simplification (heuristic suffix trimming)
# ---------------------------------------------------------------------------
# Common Uzbek inflectional/derivational suffixes, longest first.
_SUFFIXES = [
    "larimizdan", "laringizdan", "larimiz", "laringiz", "larida",
    "lardan", "larga", "larni", "lari", "lar",
    "imizdan", "ingizdan", "lariga",
    "dagi", "dagilar", "dan", "da", "ga", "ni", "ning", "nikidan",
    "miz", "ngiz", "lik", "chi", "siz", "im", "ing",
    "moqda", "yapti", "gan", "kan", "qan", "di", "ti", "yotgan",
]


def light_stem(token):
    """Trim a single common suffix if the remaining stem stays reasonably long."""
    for suf in _SUFFIXES:
        if token.endswith(suf) and len(token) - len(suf) >= 4:
            return token[: -len(suf)]
    return token


# ---------------------------------------------------------------------------
# Full pipeline
# ---------------------------------------------------------------------------
def preprocess(text, remove_stopwords=True, stem=True):
    """Return a cleaned, space-joined token string ready for vectorisation."""
    cleaned = clean_text(text)
    tokens = tokenize(cleaned)
    if remove_stopwords:
        tokens = [t for t in tokens if t not in UZBEK_STOPWORDS]
    if stem:
        tokens = [light_stem(t) for t in tokens]
    tokens = [t for t in tokens if len(t) > 1]
    return " ".join(tokens)


def preprocess_corpus(texts, **kwargs):
    return [preprocess(t, **kwargs) for t in texts]


if __name__ == "__main__":
    samples = [
        "Шифокорлар огоҳлантирмоқда: бу дори касалликни даволайди!",
        "Oʻzbekiston Markaziy banki stavkani oʻzgarishsiz qoldirdi.",
    ]
    for s in samples:
        print(repr(s), "->", repr(preprocess(s)))
