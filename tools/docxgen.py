"""
Pure-Python DOCX generator (no external dependencies).

Builds a valid .docx (OpenXML / WordprocessingML) file from a simple list of
content blocks. Created because `python-docx` is not installable in this
offline sandbox.

Formatting defaults match the university technical requirements:
  * Font:        Times New Roman, 14 pt
  * Line spacing: 1.5
  * Page size:    A4
  * Margins:      left 3 cm, right 1.5 cm, top 2 cm, bottom 2 cm

Inline markup supported inside paragraph text:
  **bold**            -> bold run
  *italic*            -> italic run

Block model (list of dicts), see build_document() docstring for keys.
"""

import os
import zipfile
from xml.sax.saxutils import escape

# ----------------------------------------------------------------------------
# Unit helpers
# ----------------------------------------------------------------------------
CM_TO_TWIP = 567          # 1 cm  = 567 twips
PT_TO_HALFPT = 2          # docx font size is in half-points

PAGE_W = 11906            # A4 width  in twips (21.0 cm)
PAGE_H = 16838            # A4 height in twips (29.7 cm)

MARGIN_LEFT = int(3.0 * CM_TO_TWIP)
MARGIN_RIGHT = int(1.5 * CM_TO_TWIP)
MARGIN_TOP = int(2.0 * CM_TO_TWIP)
MARGIN_BOTTOM = int(2.0 * CM_TO_TWIP)

LINE_15 = 360             # 1.5 line spacing (240 = single)

FONT = "Times New Roman"
BODY_HALFPT = 28          # 14 pt


# ----------------------------------------------------------------------------
# Inline run parsing (**bold**, *italic*)
# ----------------------------------------------------------------------------
def _runs_from_text(text, base_size=BODY_HALFPT, bold=False, italic=False):
    """Return XML string of <w:r> runs, honoring **bold** and *italic* markup."""
    if text is None:
        text = ""
    out = []
    i = 0
    n = len(text)
    cur_bold = bold
    cur_ital = italic
    buf = ""

    def flush():
        nonlocal buf
        if buf != "":
            out.append(_run(buf, base_size, cur_bold, cur_ital))
            buf = ""

    while i < n:
        if text.startswith("**", i):
            flush()
            cur_bold = not cur_bold
            i += 2
        elif text[i] == "*":
            flush()
            cur_ital = not cur_ital
            i += 1
        else:
            buf += text[i]
            i += 1
    flush()
    return "".join(out)


def _run(text, size=BODY_HALFPT, bold=False, italic=False, color=None):
    rpr = ['<w:rFonts w:ascii="%s" w:hAnsi="%s" w:cs="%s"/>' % (FONT, FONT, FONT)]
    if bold:
        rpr.append("<w:b/>")
    if italic:
        rpr.append("<w:i/>")
    rpr.append('<w:sz w:val="%d"/><w:szCs w:val="%d"/>' % (size, size))
    if color:
        rpr.append('<w:color w:val="%s"/>' % color)
    # preserve spaces
    t = escape(text)
    return ('<w:r><w:rPr>%s</w:rPr><w:t xml:space="preserve">%s</w:t></w:r>'
            % ("".join(rpr), t))


def _ppr(style=None, align=None, spacing_after=120, spacing_before=0,
         line=LINE_15, num_id=None, ilvl=0, page_break_before=False,
         keep_next=False, indent_left=None):
    parts = ["<w:pPr>"]
    if style:
        parts.append('<w:pStyle w:val="%s"/>' % style)
    if page_break_before:
        parts.append("<w:pageBreakBefore/>")
    if keep_next:
        parts.append("<w:keepNext/>")
    if num_id is not None:
        parts.append('<w:numPr><w:ilvl w:val="%d"/><w:numId w:val="%d"/></w:numPr>'
                     % (ilvl, num_id))
    if indent_left is not None:
        parts.append('<w:ind w:left="%d"/>' % indent_left)
    parts.append('<w:spacing w:before="%d" w:after="%d" w:line="%d" w:lineRule="auto"/>'
                 % (spacing_before, spacing_after, line))
    if align:
        parts.append('<w:jc w:val="%s"/>' % align)
    parts.append("</w:pPr>")
    return "".join(parts)


# ----------------------------------------------------------------------------
# Block renderers
# ----------------------------------------------------------------------------
def _p(text, **kw):
    align = kw.pop("align", "both")
    size = kw.pop("size", BODY_HALFPT)
    bold = kw.pop("bold", False)
    italic = kw.pop("italic", False)
    return "<w:p>%s%s</w:p>" % (_ppr(align=align, **kw),
                                _runs_from_text(text, size, bold, italic))


def _heading(text, level):
    style = "Heading%d" % level
    sizes = {1: 32, 2: 28, 3: 28}
    return ("<w:p>%s%s</w:p>"
            % (_ppr(style=style, align="left", spacing_before=240,
                    spacing_after=120, keep_next=True,
                    page_break_before=(level == 1)),
               _run(text, sizes.get(level, 28), bold=True)))


def _title(text, size=40):
    return ("<w:p>%s%s</w:p>"
            % (_ppr(align="center", spacing_after=120, spacing_before=120),
               _run(text, size, bold=True)))


def _center(text, size=BODY_HALFPT, bold=False, italic=False, after=120):
    return ("<w:p>%s%s</w:p>"
            % (_ppr(align="center", spacing_after=after),
               _runs_from_text(text, size, bold, italic)))


def _pagebreak():
    return '<w:p><w:r><w:br w:type="page"/></w:r></w:p>'


def _bullet(items, num_id=1):
    out = []
    for it in items:
        out.append("<w:p>%s%s</w:p>"
                   % (_ppr(num_id=num_id, ilvl=0, spacing_after=60),
                      _runs_from_text(it)))
    return "".join(out)


def _numbered(items, num_id=2):
    out = []
    for it in items:
        out.append("<w:p>%s%s</w:p>"
                   % (_ppr(num_id=num_id, ilvl=0, spacing_after=60),
                      _runs_from_text(it)))
    return "".join(out)


def _table(rows, header=True, widths=None):
    ncols = max(len(r) for r in rows)
    total = PAGE_W - MARGIN_LEFT - MARGIN_RIGHT
    if widths is None:
        widths = [total // ncols] * ncols
    else:
        s = sum(widths)
        widths = [int(total * w / s) for w in widths]

    grid = "".join('<w:gridCol w:w="%d"/>' % w for w in widths)
    out = ['<w:tbl><w:tblPr>'
           '<w:tblW w:w="%d" w:type="dxa"/>' % total +
           '<w:tblBorders>'
           '<w:top w:val="single" w:sz="4" w:space="0" w:color="000000"/>'
           '<w:left w:val="single" w:sz="4" w:space="0" w:color="000000"/>'
           '<w:bottom w:val="single" w:sz="4" w:space="0" w:color="000000"/>'
           '<w:right w:val="single" w:sz="4" w:space="0" w:color="000000"/>'
           '<w:insideH w:val="single" w:sz="4" w:space="0" w:color="000000"/>'
           '<w:insideV w:val="single" w:sz="4" w:space="0" w:color="000000"/>'
           '</w:tblBorders><w:tblLook w:val="04A0"/></w:tblPr>'
           '<w:tblGrid>%s</w:tblGrid>' % grid]
    for ri, row in enumerate(rows):
        is_head = header and ri == 0
        out.append("<w:tr>")
        for ci in range(ncols):
            cell = row[ci] if ci < len(row) else ""
            shade = ('<w:shd w:val="clear" w:color="auto" w:fill="D9E2F3"/>'
                     if is_head else "")
            cellp = ('<w:p>%s%s</w:p>'
                     % (_ppr(align="left", spacing_after=40, line=240),
                        _runs_from_text(str(cell), base_size=24,
                                        bold=is_head)))
            out.append('<w:tc><w:tcPr><w:tcW w:w="%d" w:type="dxa"/>%s'
                       '<w:vAlign w:val="center"/></w:tcPr>%s</w:tc>'
                       % (widths[ci], shade, cellp))
        out.append("</w:tr>")
    out.append("</w:tbl>")
    # a trailing empty paragraph so Word doesn't choke when table ends doc/section
    out.append('<w:p><w:pPr><w:spacing w:after="120" w:line="%d" '
               'w:lineRule="auto"/></w:pPr></w:p>' % LINE_15)
    return "".join(out)


# Right tab position for TOC dot leaders (text width = page - margins)
TOC_TAB = PAGE_W - MARGIN_LEFT - MARGIN_RIGHT
LINES_PER_PAGE = 32


def _toc_entry_runs(text, page, level, with_field=None):
    """Build the runs for a single TOC entry: text <tab+dotleader> page.

    with_field: None, "begin" (this entry opens the field), or
    "end" (this entry closes the field).
    """
    bold = level == 0
    runs = []
    if with_field == "begin":
        runs.append('<w:r><w:fldChar w:fldCharType="begin"/></w:r>')
        runs.append('<w:r><w:instrText xml:space="preserve"> TOC \\o "1-3" \\h \\z \\u </w:instrText></w:r>')
        runs.append('<w:r><w:fldChar w:fldCharType="separate"/></w:r>')
    runs.append(_run(text, BODY_HALFPT, bold=bold))
    runs.append('<w:r><w:rPr><w:rFonts w:ascii="%s" w:hAnsi="%s"/>'
                '<w:sz w:val="%d"/></w:rPr><w:tab/></w:r>' % (FONT, FONT, BODY_HALFPT))
    runs.append(_run(str(page), BODY_HALFPT, bold=bold))
    if with_field == "end":
        runs.append('<w:r><w:fldChar w:fldCharType="end"/></w:r>')
    return "".join(runs)


def _toc(entries):
    """Insert a fully populated Table of Contents.

    `entries` is a list of (level, text, page). The result is a live Word TOC
    field whose cached content already lists every heading with dot leaders and
    page numbers, so it displays immediately and still updates (F9) in Word.
    """
    if not entries:
        return ""
    out = []
    n = len(entries)
    for i, (level, text, page) in enumerate(entries):
        style = "TOC%d" % (level + 1)
        if i == 0:
            field = "begin"
        elif i == n - 1:
            field = "end"
        else:
            field = None
        ppr = ('<w:pPr><w:pStyle w:val="%s"/>'
               '<w:tabs><w:tab w:val="right" w:leader="dot" w:pos="%d"/></w:tabs>'
               '<w:spacing w:after="60" w:line="%d" w:lineRule="auto"/></w:pPr>'
               % (style, TOC_TAB, LINE_15))
        out.append("<w:p>%s%s</w:p>"
                   % (ppr, _toc_entry_runs(text, page, level, field)))
    return "".join(out)


def _estimate_pages(blocks):
    """Estimate the page on which each heading begins, accounting for the
    H1 page-breaks and explicit page breaks. Used to pre-fill the TOC; Word
    recomputes exact numbers when the field is updated."""
    headings_total = sum(1 for b in blocks if b["type"] in ("h1", "h2", "h3"))
    toc_lines = headings_total + 3

    def words(s):
        return max(1, len(s.split()))

    page = 1
    line = 0.0
    entries = []

    def add(cost):
        nonlocal page, line
        line += cost
        while line > LINES_PER_PAGE:
            line -= LINES_PER_PAGE
            page += 1

    for b in blocks:
        t = b["type"]
        if t == "pagebreak":
            page += 1
            line = 0.0
        elif t == "title":
            add(4)
        elif t == "center":
            add(1.2)
        elif t == "h1":
            if line > 0:               # pageBreakBefore behaviour
                page += 1
                line = 0.0
            entries.append((0, b["text"], page))
            add(2.4)
        elif t == "h2":
            if line + 2 > LINES_PER_PAGE:
                page += 1
                line = 0.0
            entries.append((1, b["text"], page))
            add(2.0)
        elif t == "h3":
            if line + 2 > LINES_PER_PAGE:
                page += 1
                line = 0.0
            entries.append((2, b["text"], page))
            add(2.0)
        elif t == "p":
            add(max(1.0, (words(b["text"]) / 12.0)) + 0.6)
        elif t == "bullet" or t == "num":
            for it in b["items"]:
                add(max(1.0, words(it) / 12.0) + 0.3)
        elif t == "table":
            add(len(b["rows"]) * 1.4 + 2)
        elif t == "caption":
            add(1.5)
        elif t == "toc":
            add(toc_lines)
    return entries


def _caption(text):
    return ("<w:p>%s%s</w:p>"
            % (_ppr(align="center", spacing_after=160, line=240),
               _runs_from_text(text, base_size=22, italic=True)))


# ----------------------------------------------------------------------------
# Document assembly
# ----------------------------------------------------------------------------
def render_blocks(blocks):
    toc_entries = _estimate_pages(blocks)
    body = []
    for b in blocks:
        t = b["type"]
        if t == "title":
            body.append(_title(b["text"], b.get("size", 40)))
        elif t == "center":
            body.append(_center(b["text"], b.get("size", BODY_HALFPT),
                                 b.get("bold", False), b.get("italic", False),
                                 b.get("after", 120)))
        elif t == "h1":
            body.append(_heading(b["text"], 1))
        elif t == "h2":
            body.append(_heading(b["text"], 2))
        elif t == "h3":
            body.append(_heading(b["text"], 3))
        elif t == "p":
            body.append(_p(b["text"], align=b.get("align", "both")))
        elif t == "bullet":
            body.append(_bullet(b["items"]))
        elif t == "num":
            body.append(_numbered(b["items"]))
        elif t == "table":
            body.append(_table(b["rows"], b.get("header", True),
                               b.get("widths")))
        elif t == "caption":
            body.append(_caption(b["text"]))
        elif t == "pagebreak":
            body.append(_pagebreak())
        elif t == "toc":
            body.append(_toc(toc_entries))
        else:
            raise ValueError("unknown block type: %r" % t)
    return "".join(body)


SECT_PR = (
    '<w:sectPr>'
    '<w:pgSz w:w="%d" w:h="%d"/>'
    '<w:pgMar w:top="%d" w:right="%d" w:bottom="%d" w:left="%d" '
    'w:header="708" w:footer="708" w:gutter="0"/>'
    '<w:pgNumType w:start="1"/>'
    '</w:sectPr>' % (PAGE_W, PAGE_H, MARGIN_TOP, MARGIN_RIGHT,
                     MARGIN_BOTTOM, MARGIN_LEFT)
)


def _document_xml(blocks):
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
        '<w:body>%s%s</w:body></w:document>'
        % (render_blocks(blocks), SECT_PR)
    )


def _styles_xml():
    base_rpr = ('<w:rFonts w:ascii="%s" w:hAnsi="%s" w:cs="%s"/>'
                '<w:sz w:val="%d"/><w:szCs w:val="%d"/>'
                % (FONT, FONT, FONT, BODY_HALFPT, BODY_HALFPT))
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        '<w:docDefaults><w:rPrDefault><w:rPr>%s</w:rPr></w:rPrDefault>'
        '<w:pPrDefault><w:pPr><w:spacing w:after="120" w:line="%d" w:lineRule="auto"/></w:pPr></w:pPrDefault>'
        '</w:docDefaults>'
        # Normal
        '<w:style w:type="paragraph" w:default="1" w:styleId="Normal">'
        '<w:name w:val="Normal"/><w:rPr>%s</w:rPr></w:style>'
        # Heading 1
        '<w:style w:type="paragraph" w:styleId="Heading1"><w:name w:val="heading 1"/>'
        '<w:basedOn w:val="Normal"/><w:next w:val="Normal"/>'
        '<w:pPr><w:keepNext/><w:outlineLvl w:val="0"/></w:pPr>'
        '<w:rPr><w:rFonts w:ascii="%s" w:hAnsi="%s"/><w:b/><w:sz w:val="32"/><w:szCs w:val="32"/></w:rPr></w:style>'
        # Heading 2
        '<w:style w:type="paragraph" w:styleId="Heading2"><w:name w:val="heading 2"/>'
        '<w:basedOn w:val="Normal"/><w:next w:val="Normal"/>'
        '<w:pPr><w:keepNext/><w:outlineLvl w:val="1"/></w:pPr>'
        '<w:rPr><w:rFonts w:ascii="%s" w:hAnsi="%s"/><w:b/><w:sz w:val="28"/><w:szCs w:val="28"/></w:rPr></w:style>'
        # Heading 3
        '<w:style w:type="paragraph" w:styleId="Heading3"><w:name w:val="heading 3"/>'
        '<w:basedOn w:val="Normal"/><w:next w:val="Normal"/>'
        '<w:pPr><w:keepNext/><w:outlineLvl w:val="2"/></w:pPr>'
        '<w:rPr><w:rFonts w:ascii="%s" w:hAnsi="%s"/><w:b/><w:i/><w:sz w:val="28"/><w:szCs w:val="28"/></w:rPr></w:style>'
        # TOC 1 / 2 / 3
        '<w:style w:type="paragraph" w:styleId="TOC1"><w:name w:val="toc 1"/>'
        '<w:basedOn w:val="Normal"/><w:next w:val="Normal"/>'
        '<w:pPr><w:spacing w:after="60"/></w:pPr>'
        '<w:rPr><w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman"/><w:b/></w:rPr></w:style>'
        '<w:style w:type="paragraph" w:styleId="TOC2"><w:name w:val="toc 2"/>'
        '<w:basedOn w:val="Normal"/><w:next w:val="Normal"/>'
        '<w:pPr><w:spacing w:after="60"/><w:ind w:left="360"/></w:pPr>'
        '<w:rPr><w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman"/></w:rPr></w:style>'
        '<w:style w:type="paragraph" w:styleId="TOC3"><w:name w:val="toc 3"/>'
        '<w:basedOn w:val="Normal"/><w:next w:val="Normal"/>'
        '<w:pPr><w:spacing w:after="60"/><w:ind w:left="720"/></w:pPr>'
        '<w:rPr><w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman"/></w:rPr></w:style>'
        '</w:styles>'
        % (base_rpr, LINE_15, base_rpr, FONT, FONT, FONT, FONT, FONT, FONT)
    )


def _numbering_xml():
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:numbering xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        # abstract 0: bullet
        '<w:abstractNum w:abstractNumId="0"><w:lvl w:ilvl="0">'
        '<w:start w:val="1"/><w:numFmt w:val="bullet"/><w:lvlText w:val="\u2022"/>'
        '<w:lvlJc w:val="left"/><w:pPr><w:ind w:left="720" w:hanging="360"/></w:pPr>'
        '<w:rPr><w:rFonts w:ascii="Symbol" w:hAnsi="Symbol"/></w:rPr></w:lvl></w:abstractNum>'
        # abstract 1: decimal
        '<w:abstractNum w:abstractNumId="1"><w:lvl w:ilvl="0">'
        '<w:start w:val="1"/><w:numFmt w:val="decimal"/><w:lvlText w:val="%1."/>'
        '<w:lvlJc w:val="left"/><w:pPr><w:ind w:left="720" w:hanging="360"/></w:pPr></w:lvl></w:abstractNum>'
        '<w:num w:numId="1"><w:abstractNumId w:val="0"/></w:num>'
        '<w:num w:numId="2"><w:abstractNumId w:val="1"/></w:num>'
        '</w:numbering>'
    )


def _settings_xml():
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:settings xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        '<w:updateFields w:val="true"/>'
        '<w:defaultTabStop w:val="708"/></w:settings>'
    )


CONTENT_TYPES = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
    '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
    '<Default Extension="xml" ContentType="application/xml"/>'
    '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
    '<Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>'
    '<Override PartName="/word/numbering.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.numbering+xml"/>'
    '<Override PartName="/word/settings.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.settings+xml"/>'
    '</Types>'
)

RELS = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
    '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>'
    '</Relationships>'
)

DOC_RELS = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
    '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>'
    '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/numbering" Target="numbering.xml"/>'
    '<Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/settings" Target="settings.xml"/>'
    '</Relationships>'
)


def build_document(blocks, out_path):
    """Write a .docx file from a list of content blocks.

    Block dict shapes:
      {"type":"title",  "text": str, "size"?: halfpt}
      {"type":"center", "text": str, "bold"?, "italic"?, "size"?, "after"?}
      {"type":"h1"/"h2"/"h3", "text": str}
      {"type":"p", "text": str, "align"?: both|left|center|right}
      {"type":"bullet", "items": [str,...]}
      {"type":"num",    "items": [str,...]}
      {"type":"table",  "rows": [[..],..], "header"?: bool, "widths"?: [..]}
      {"type":"caption","text": str}
      {"type":"pagebreak"}
      {"type":"toc"}
    """
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", CONTENT_TYPES)
        z.writestr("_rels/.rels", RELS)
        z.writestr("word/_rels/document.xml.rels", DOC_RELS)
        z.writestr("word/document.xml", _document_xml(blocks))
        z.writestr("word/styles.xml", _styles_xml())
        z.writestr("word/numbering.xml", _numbering_xml())
        z.writestr("word/settings.xml", _settings_xml())
    return out_path


if __name__ == "__main__":
    demo = [
        {"type": "title", "text": "DOCX Generator Self-Test"},
        {"type": "center", "text": "Times New Roman 14, 1.5 spacing", "italic": True},
        {"type": "h1", "text": "Chapter 1 - Introduction"},
        {"type": "p", "text": "This is a **bold** word and an *italic* word in a justified paragraph."},
        {"type": "h2", "text": "1.1 A Subsection"},
        {"type": "bullet", "items": ["First point", "Second point"]},
        {"type": "table", "rows": [["Model", "F1"], ["SVM", "0.91"]]},
        {"type": "caption", "text": "Table 1. Demo table."},
    ]
    build_document(demo, "tools/_selftest.docx")
    print("wrote tools/_selftest.docx")
