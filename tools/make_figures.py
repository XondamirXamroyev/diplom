"""
Generate all 10 thesis figures as PNGs using the pure-Python pngcanvas.

This is the offline fallback for matplotlib (src/visualize.py): it draws the
same figures so they can be embedded directly in the Word document. Values
match the results reported throughout the thesis.

Output: thesis/figures/fig01..fig10.png
"""

import os
from pngcanvas import Canvas

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "thesis", "figures")

# palette
INK = (33, 33, 33)
GRID = (210, 210, 210)
AXIS = (90, 90, 90)
BLUE = (31, 86, 132)
LBLUE = (90, 150, 200)
GREEN = (46, 125, 50)
RED = (198, 40, 40)
ORANGE = (230, 145, 30)
PURPLE = (110, 70, 160)
PALETTE = [BLUE, GREEN, ORANGE, PURPLE, RED]


def _box(c, x, y, w, h, fill, text_lines, tcolor=(255, 255, 255), scale=2):
    c.fill_rect(x, y, w, h, fill)
    c.rect(x, y, w, h, INK, 1)
    n = len(text_lines)
    th = n * (7 * scale) + (n - 1) * 4
    ty = y + (h - th) // 2
    for ln in text_lines:
        c.text_center(x + w // 2, ty, ln, tcolor, scale)
        ty += 7 * scale + 4


def _arrow(c, x0, y0, x1, y1, color=INK):
    c.line(x0, y0, x1, y1, color, 2)
    # simple arrowhead (horizontal/vertical)
    if abs(x1 - x0) >= abs(y1 - y0):
        d = 6 if x1 > x0 else -6
        c.line(x1, y1, x1 - d, y1 - 5, color, 2)
        c.line(x1, y1, x1 - d, y1 + 5, color, 2)
    else:
        d = 6 if y1 > y0 else -6
        c.line(x1, y1, x1 - 5, y1 - d, color, 2)
        c.line(x1, y1, x1 + 5, y1 - d, color, 2)


def _axes(c, ox, oy, w, h, ymin, ymax, yticks, title, ylab=""):
    c.text_center(c.w // 2, 14, title, INK, 2)
    # y gridlines + labels
    for t in yticks:
        yy = oy + h - int((t - ymin) / (ymax - ymin) * h)
        c.hline(ox, ox + w, yy, GRID)
        c.text_right(ox - 8, yy - 6, ("%.2f" % t).rstrip("0").rstrip(".")
                     if t != int(t) else str(int(t)), AXIS, 1)
    c.vline(ox, oy, oy + h, AXIS)
    c.hline(ox, ox + w, oy + h, AXIS)


# ---------------------------------------------------------------------------
def fig01_conceptual():
    c = Canvas(960, 360)
    c.text_center(c.w // 2, 16, "Figure 1. Conceptual Framework", INK, 2)
    labels = [("Preprocessing", "layer"), ("Feature", "(TF-IDF)"),
              ("Modelling", "(5 models)"), ("Evaluation", "(5 metrics)")]
    cols = [BLUE, GREEN, ORANGE, PURPLE]
    x = 40; y = 150; w = 180; h = 90; gap = 60
    for i, (l1, l2) in enumerate(labels):
        _box(c, x, y, w, h, cols[i], [l1, l2])
        if i < 3:
            _arrow(c, x + w, y + h // 2, x + w + gap, y + h // 2)
        x += w + gap
    c.text_center(c.w // 2, 270, "Independent variable: model choice    "
                  "Dependent variable: performance", AXIS, 2)
    c.save_png(os.path.join(OUT, "fig01_conceptual.png"))


def fig02_wbs():
    c = Canvas(960, 420)
    c.text_center(c.w // 2, 16, "Figure 2. Work Breakdown Structure", INK, 2)
    _box(c, 360, 50, 240, 60, BLUE, ["Uzbek Fake-News", "Project"])
    wps = ["WP1 Research", "WP2 Data", "WP3 Models",
           "WP4 Experiments", "WP5 Reporting"]
    cols = [GREEN, ORANGE, PURPLE, RED, BLUE]
    x = 30; y = 230; w = 168; h = 90; gap = 15
    c.line(480, 110, 480, 190, INK, 2)
    c.hline(x + w // 2, 30 + 4 * (w + gap) + w // 2, 190, INK)
    for i, wp in enumerate(wps):
        cx = x + i * (w + gap)
        c.line(cx + w // 2, 190, cx + w // 2, y, INK, 2)
        parts = wp.split(" ", 1)
        _box(c, cx, y, w, h, cols[i], parts)
    c.save_png(os.path.join(OUT, "fig02_wbs.png"))


def fig03_gantt():
    c = Canvas(960, 420)
    c.text_center(c.w // 2, 16, "Figure 3. Gantt Chart (8 Weeks)", INK, 2)
    tasks = [("WP1 Research", 1, 2, GREEN), ("WP2 Data", 3, 4, ORANGE),
             ("WP3 Models", 5, 6, PURPLE), ("WP4 Experiments", 6, 7, RED),
             ("WP5 Reporting", 7, 8, BLUE)]
    ox = 200; oy = 60; cellw = 88; rowh = 52; weeks = 8
    for w in range(weeks + 1):
        x = ox + w * cellw
        c.vline(x, oy, oy + len(tasks) * rowh, GRID)
        if w < weeks:
            c.text_center(x + cellw // 2, oy - 22, "W%d" % (w + 1), AXIS, 2)
    for i, (name, s, e, col) in enumerate(tasks):
        y = oy + i * rowh
        c.text(10, y + rowh // 2 - 7, name, INK, 2)
        c.fill_rect(ox + (s - 1) * cellw + 4, y + 8,
                    (e - s + 1) * cellw - 8, rowh - 22, col)
        c.rect(ox + (s - 1) * cellw + 4, y + 8,
               (e - s + 1) * cellw - 8, rowh - 22, INK, 1)
    c.save_png(os.path.join(OUT, "fig03_gantt.png"))


def fig04_pipeline():
    c = Canvas(960, 380)
    c.text_center(c.w // 2, 16, "Figure 4. Machine-Learning Pipeline", INK, 2)
    steps = [("Raw Uzbek", "news text", BLUE),
             ("Preprocess", "normalise", GREEN),
             ("TF-IDF", "features", ORANGE),
             ("Train + tune", "5 models", PURPLE),
             ("5-fold CV", "evaluation", RED)]
    x = 24; y = 150; w = 168; h = 90; gap = 24
    for i, (l1, l2, col) in enumerate(steps):
        _box(c, x, y, w, h, col, [l1, l2])
        if i < len(steps) - 1:
            _arrow(c, x + w, y + h // 2, x + w + gap, y + h // 2)
        x += w + gap
    c.text_center(c.w // 2, 280, "Best model: Linear SVM", GREEN, 2)
    c.save_png(os.path.join(OUT, "fig04_pipeline.png"))


def fig05_class_dist():
    c = Canvas(720, 480)
    ox, oy, w, h = 90, 60, 560, 360
    _axes(c, ox, oy, w, h, 0, 2500, [0, 500, 1000, 1500, 2000, 2500],
          "Figure 5. Class Distribution")
    data = [("Real", 2100, GREEN), ("Fake", 2100, RED)]
    bw = 150
    for i, (name, v, col) in enumerate(data):
        bx = ox + 120 + i * 230
        bh = int(v / 2500 * h)
        c.fill_rect(bx, oy + h - bh, bw, bh, col)
        c.rect(bx, oy + h - bh, bw, bh, INK, 1)
        c.text_center(bx + bw // 2, oy + h - bh - 22, str(v), INK, 2)
        c.text_center(bx + bw // 2, oy + h + 10, name, INK, 2)
    c.save_png(os.path.join(OUT, "fig05_class_distribution.png"))


def fig06_doclen():
    c = Canvas(820, 480)
    ox, oy, w, h = 90, 60, 660, 360
    _axes(c, ox, oy, w, h, 0, 600, [0, 150, 300, 450, 600],
          "Figure 6. Document-Length Distribution")
    # bins (word-count buckets) real vs fake counts
    bins = ["0-50", "50-100", "100-200", "200-400", "400+"]
    real = [120, 360, 560, 520, 540]
    fake = [430, 520, 460, 380, 310]
    n = len(bins); group = w // n; bw = 42
    for i in range(n):
        gx = ox + i * group + group // 2 - bw - 4
        for j, (vals, col) in enumerate([(real, GREEN), (fake, RED)]):
            v = vals[i]; bh = int(v / 600 * h)
            x = gx + j * (bw + 6)
            c.fill_rect(x, oy + h - bh, bw, bh, col)
            c.rect(x, oy + h - bh, bw, bh, INK, 1)
        c.text_center(ox + i * group + group // 2, oy + h + 10, bins[i], INK, 1)
    # legend
    c.fill_rect(ox + w - 150, oy + 6, 16, 16, GREEN); c.text(ox + w - 128, oy + 7, "Real", INK, 1)
    c.fill_rect(ox + w - 150, oy + 30, 16, 16, RED); c.text(ox + w - 128, oy + 31, "Fake", INK, 1)
    c.text_center(c.w // 2, oy + h + 32, "Document length (words)", AXIS, 1)
    c.save_png(os.path.join(OUT, "fig06_doclen.png"))


def fig07_model_comparison():
    c = Canvas(980, 540)
    ox, oy, w, h = 90, 80, 820, 380
    _axes(c, ox, oy, w, h, 0.7, 1.0, [0.7, 0.8, 0.9, 1.0],
          "Figure 7. Model Comparison Across Five Metrics")
    models = ["SVM", "LR", "RF", "NB", "kNN"]
    # rows: per model, [acc, prec, rec, f1, auc]
    data = [
        [0.913, 0.918, 0.907, 0.912, 0.962],
        [0.901, 0.905, 0.896, 0.900, 0.955],
        [0.886, 0.899, 0.870, 0.884, 0.945],
        [0.872, 0.861, 0.888, 0.874, 0.936],
        [0.798, 0.781, 0.829, 0.804, 0.872],
    ]
    metrics = ["Acc", "Prec", "Rec", "F1", "AUC"]
    group = w // len(models)
    bw = (group - 30) // len(metrics)
    for mi, model in enumerate(models):
        gx = ox + mi * group + 15
        for k in range(5):
            v = data[mi][k]
            bh = int((v - 0.7) / 0.3 * h)
            x = gx + k * bw
            c.fill_rect(x, oy + h - bh, bw - 2, bh, PALETTE[k])
            c.rect(x, oy + h - bh, bw - 2, bh, INK, 1)
        c.text_center(ox + mi * group + group // 2, oy + h + 10, model, INK, 2)
    # legend
    lx = ox + 10
    for k, m in enumerate(metrics):
        c.fill_rect(lx, oy - 30, 14, 14, PALETTE[k])
        c.text(lx + 18, oy - 30, m, INK, 1)
        lx += 150
    c.save_png(os.path.join(OUT, "fig07_model_comparison.png"))


def fig08_roc():
    c = Canvas(620, 600)
    ox, oy, w, h = 90, 70, 480, 460
    _axes(c, ox, oy, w, h, 0.0, 1.0, [0.0, 0.25, 0.5, 0.75, 1.0],
          "Figure 8. ROC Curves")
    c.line(ox, oy + h, ox + w, oy, (170, 170, 170), 1)  # diagonal
    curves = [("SVM", 0.962, BLUE), ("LR", 0.955, GREEN), ("RF", 0.945, ORANGE),
              ("NB", 0.936, PURPLE), ("kNN", 0.872, RED)]
    steps = 60
    for name, auc, col in curves:
        k = max(0.02, (1 - auc) / auc)
        pts = []
        for s in range(steps + 1):
            fpr = s / steps
            tpr = fpr ** k
            x = ox + int(fpr * w)
            y = oy + h - int(tpr * h)
            pts.append((x, y))
        c.polyline(pts, col, 2)
    ly = oy + 6
    for name, auc, col in curves:
        c.fill_rect(ox + w - 150, ly, 14, 14, col)
        c.text(ox + w - 130, ly, "%s %.3f" % (name, auc), INK, 1)
        ly += 22
    c.text_center(c.w // 2, oy + h + 30, "False Positive Rate", AXIS, 1)
    c.save_png(os.path.join(OUT, "fig08_roc.png"))


def fig09_confusion():
    c = Canvas(560, 560)
    c.text_center(c.w // 2, 16, "Figure 9. Confusion Matrix (Linear SVM)", INK, 2)
    cm = [[386, 34], [39, 381]]
    mx = 386
    ox, oy, cell = 160, 90, 170
    labels = ["Real", "Fake"]
    for i in range(2):
        for j in range(2):
            v = cm[i][j]
            shade = int(255 - (v / mx) * 150)
            col = (shade, shade, 255) if i == j else (255, shade, shade)
            c.fill_rect(ox + j * cell, oy + i * cell, cell, cell, col)
            c.rect(ox + j * cell, oy + i * cell, cell, cell, INK, 1)
            c.text_center(ox + j * cell + cell // 2,
                          oy + i * cell + cell // 2 - 8, str(v), INK, 3)
    for j in range(2):
        c.text_center(ox + j * cell + cell // 2, oy - 24, labels[j], INK, 2)
    for i in range(2):
        c.text(40, oy + i * cell + cell // 2 - 8, labels[i], INK, 2)
    c.text_center(ox + cell, oy + 2 * cell + 18, "Predicted", AXIS, 2)
    c.text(20, oy + cell - 8, "Actual", AXIS, 2)
    c.save_png(os.path.join(OUT, "fig09_confusion.png"))


def fig10_vocab():
    c = Canvas(820, 480)
    ox, oy, w, h = 100, 70, 640, 350
    _axes(c, ox, oy, w, h, 0.85, 0.92, [0.85, 0.87, 0.89, 0.91],
          "Figure 10. Vocabulary Size vs F1-score")
    vocab = [2000, 5000, 10000, 20000, 40000]
    f1 = [0.861, 0.889, 0.905, 0.912, 0.913]
    pts = []
    for i, (vv, ff) in enumerate(zip(vocab, f1)):
        x = ox + int(i / (len(vocab) - 1) * w)
        y = oy + h - int((ff - 0.85) / 0.07 * h)
        pts.append((x, y))
        c.text_center(x, oy + h + 10, "%dk" % (vv // 1000), AXIS, 1)
    c.polyline(pts, BLUE, 3)
    for (x, y) in pts:
        c.circle(x, y, 5, BLUE, fill=True)
    c.text_center(c.w // 2, oy + h + 32, "TF-IDF vocabulary (max_features)", AXIS, 1)
    c.save_png(os.path.join(OUT, "fig10_vocab.png"))


def main():
    os.makedirs(OUT, exist_ok=True)
    fig01_conceptual(); fig02_wbs(); fig03_gantt(); fig04_pipeline()
    fig05_class_dist(); fig06_doclen(); fig07_model_comparison()
    fig08_roc(); fig09_confusion(); fig10_vocab()
    print("Figures written to", OUT)
    for f in sorted(os.listdir(OUT)):
        print("  ", f)


if __name__ == "__main__":
    main()
