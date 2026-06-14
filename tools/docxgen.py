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


def _toc():
    """Insert a Table of Contents field (Word updates it on open / F9)."""
    return (
        '<w:p><w:pPr><w:spacing w:after="120" w:line="%d" w:lineRule="auto"/>'
        '</w:pPr>'
        '<w:r><w:fldChar w:fldCharType="begin"/></w:r>'
        '<w:r><w:instrText xml:space="preserve"> TOC \\o "1-3" \\h \\z \\u </w:instrText></w:r>'
        '<w:r><w:fldChar w:fldCharType="separate"/></w:r>'
        '<w:r><w:rPr><w:rFonts w:ascii="%s" w:hAnsi="%s"/><w:sz w:val="%d"/></w:rPr>'
        '<w:t xml:space="preserve">Right-click and choose "Update Field" to build the table of contents.</w:t></w:r>'
        '<w:r><w:fldChar w:fldCharType="end"/></w:r></w:p>'
        % (LINE_15, FONT, FONT, BODY_HALFPT))


def _caption(text):
    return ("<w:p>%s%s</w:p>"
            % (_ppr(align="center", spacing_after=160, line=240),
               _runs_from_text(text, base_size=22, italic=True)))


# ----------------------------------------------------------------------------
# Document assembly
# ----------------------------------------------------------------------------
def render_blocks(blocks):
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
            body.append(_toc())
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
