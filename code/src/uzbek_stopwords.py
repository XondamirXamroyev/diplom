"""
A compact Uzbek (Latin-script) stop-word list.

Stop words are very frequent function words (conjunctions, pronouns,
postpositions, particles) that carry little class-discriminative signal in a
bag-of-words / TF-IDF representation. Removing them reduces noise and feature
dimensionality. The list is intentionally conservative; extend it as needed.
"""

UZBEK_STOPWORDS = {
    # pronouns
    "men", "sen", "u", "biz", "siz", "ular", "meni", "seni", "uni",
    "bizni", "sizni", "ularni", "mening", "sening", "uning", "bizning",
    "sizning", "ularning", "oʻz", "oz", "bu", "shu", "ushbu", "oʻsha",
    "osha", "ana", "mana", "kim", "nima", "qaysi", "qanday", "qancha",
    # conjunctions / particles
    "va", "ham", "hamda", "yoki", "yoxud", "lekin", "ammo", "biroq",
    "chunki", "agar", "agarda", "garchi", "shuningdek", "bilan", "uchun",
    "kabi", "singari", "yana", "faqat", "balki", "esa", "ya'ni", "yani",
    "deb", "deya", "degan", "deydi", "dedi",
    # postpositions / adverbs of place-time
    "uchun", "tomon", "tomonidan", "boʻyicha", "boyicha", "haqida",
    "haqidagi", "orqali", "keyin", "oldin", "soʻng", "song", "hozir",
    "endi", "doim", "hamma", "barcha", "har", "ba'zi", "bazi", "bir",
    "ikki", "koʻp", "kop", "oz", "juda", "eng", "yaqin", "uzoq",
    # copula / auxiliary fragments
    "edi", "ekan", "emas", "boʻldi", "boldi", "boʻlgan", "bolgan",
    "boʻlib", "bolib", "boʻladi", "boladi", "qildi", "qiladi", "qilgan",
    "bor", "yoʻq", "yoq", "kerak", "mumkin",
    # discourse
    "ya'ni", "masalan", "albatta", "demak", "xullas", "umuman",
    "shu", "shuning", "shunday", "buning", "uningcha",
}
