"""
Pure-Python PPTX generator (no external dependencies).

Builds a valid 16:9 .pptx from a simple list of slide specs. Created because
`python-pptx` is not installable in this offline sandbox.

Slide spec (dict):
  {"title": str,
   "subtitle": str (optional, for the title slide),
   "bullets": [ (text, level) | text, ... ]  (optional),
   "table": {"headers":[...], "rows":[[...],...]}  (optional),
   "footer": str (optional)}

Colours and a single master/layout are defined inline. Each slide is rendered
with explicit text boxes (no reliance on placeholder inheritance) for maximum
compatibility with PowerPoint, Keynote and LibreOffice Impact/Impress.
"""

import os
import zipfile
from xml.sax.saxutils import escape

# 16:9 slide size in EMU (English Metric Units): 13.333in x 7.5in
SLIDE_W = 12192000
SLIDE_H = 6858000
EMU = 914400  # per inch

# palette
C_PRIMARY = "1F3864"     # dark blue
C_ACCENT = "2E74B5"      # medium blue
C_TEXT = "222222"
C_LIGHT = "FFFFFF"
C_BAND = "1F3864"
C_GREEN = "2E7D32"

FONT = "Calibri"


def _emu_in(v):
    return int(v * EMU)


# ---------------------------------------------------------------------------
# run / paragraph builders (DrawingML text)
# ---------------------------------------------------------------------------
def _run(text, size_pt, bold=False, color=C_TEXT, italic=False):
    b = ' b="1"' if bold else ""
    it = ' i="1"' if italic else ""
    return ('<a:r><a:rPr lang="en-US" sz="%d"%s%s dirty="0">'
            '<a:solidFill><a:srgbClr val="%s"/></a:solidFill>'
            '<a:latin typeface="%s"/></a:rPr>'
            '<a:t>%s</a:t></a:r>'
            % (int(size_pt * 100), b, it, color, FONT, escape(text)))


def _para(runs_xml, level=0, bullet=False, size_pt=18, align="l", space_after=600):
    bu = ('<a:buFont typeface="Arial"/><a:buChar char="\u2022"/>'
          if bullet else "<a:buNone/>")
    return ('<a:p><a:pPr lvl="%d" algn="%s" marL="%d" indent="%d">'
            '<a:spcBef><a:spcPts val="%d"/></a:spcBef>%s</a:pPr>%s</a:p>'
            % (level, align, 342900 * level + (274320 if bullet else 0),
               -274320 if bullet else 0, space_after, bu, runs_xml))


def _textbox(shape_id, name, x, y, w, h, paragraphs_xml, anchor="t"):
    return (
        '<p:sp><p:nvSpPr><p:cNvPr id="%d" name="%s"/>'
        '<p:cNvSpPr txBox="1"/><p:nvPr/></p:nvSpPr>'
        '<p:spPr><a:xfrm><a:off x="%d" y="%d"/><a:ext cx="%d" cy="%d"/></a:xfrm>'
        '<a:prstGeom prst="rect"><a:avLst/></a:prstGeom></p:spPr>'
        '<p:txBody><a:bodyPr wrap="square" anchor="%s"><a:normAutofit/></a:bodyPr>'
        '<a:lstStyle/>%s</p:txBody></p:sp>'
        % (shape_id, name, x, y, w, h, anchor, paragraphs_xml)
    )


def _rect(shape_id, name, x, y, w, h, fill):
    return (
        '<p:sp><p:nvSpPr><p:cNvPr id="%d" name="%s"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>'
        '<p:spPr><a:xfrm><a:off x="%d" y="%d"/><a:ext cx="%d" cy="%d"/></a:xfrm>'
        '<a:prstGeom prst="rect"><a:avLst/></a:prstGeom>'
        '<a:solidFill><a:srgbClr val="%s"/></a:solidFill>'
        '<a:ln><a:noFill/></a:ln></p:spPr>'
        '<p:txBody><a:bodyPr/><a:lstStyle/><a:p><a:endParaRPr/></a:p></p:txBody></p:sp>'
        % (shape_id, name, x, y, w, h, fill)
    )


def _table(shape_id, x, y, w, headers, rows):
    ncol = len(headers)
    colw = w // ncol
    grid = "".join('<a:gridCol w="%d"/>' % colw for _ in range(ncol))

    def cell(text, bold=False, fill=None, color=C_TEXT, size=12):
        shade = ('<a:solidFill><a:srgbClr val="%s"/></a:solidFill>' % fill) if fill else "<a:noFill/>"
        return ('<a:tc><a:txBody><a:bodyPr/><a:lstStyle/>'
                '<a:p><a:pPr algn="ctr"/>%s</a:p></a:txBody>'
                '<a:tcPr marL="45720" marR="45720" marT="22860" marB="22860" anchor="ctr">%s</a:tcPr></a:tc>'
                % (_run(str(text), size, bold=bold, color=color), shade))

    trs = []
    # header row
    trs.append('<a:tr h="370840">' +
               "".join(cell(h, bold=True, fill=C_PRIMARY, color=C_LIGHT, size=13)
                       for h in headers) + "</a:tr>")
    for ri, r in enumerate(rows):
        band = "DCE6F1" if ri % 2 == 0 else "FFFFFF"
        # highlight best row (first data row) in light green
        if ri == 0:
            band = "C8E6C9"
        trs.append('<a:tr h="320040">' +
                   "".join(cell(c, fill=band, size=12) for c in r) + "</a:tr>")

    return (
        '<p:graphicFrame><p:nvGraphicFramePr><p:cNvPr id="%d" name="ResultsTable"/>'
        '<p:cNvGraphicFramePr/><p:nvPr/></p:nvGraphicFramePr>'
        '<p:xfrm><a:off x="%d" y="%d"/><a:ext cx="%d" cy="%d"/></p:xfrm>'
        '<a:graphic><a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/table">'
        '<a:tbl><a:tblPr firstRow="1" bandRow="1"/>'
        '<a:tblGrid>%s</a:tblGrid>%s</a:tbl></a:graphicData></a:graphic></p:graphicFrame>'
        % (shape_id, x, y, w, 370840 + len(rows) * 320040, grid, "".join(trs))
    )


# ---------------------------------------------------------------------------
# slide rendering
# ---------------------------------------------------------------------------
def _slide_xml(spec, index, total):
    shapes = []
    sid = 2

    is_title = spec.get("layout") == "title"

    if is_title:
        # full background band
        shapes.append(_rect(sid, "bg", 0, 0, SLIDE_W, SLIDE_H, C_PRIMARY)); sid += 1
        # title
        title_p = _para(_run(spec["title"], 40, bold=True, color=C_LIGHT),
                        align="ctr", space_after=0)
        shapes.append(_textbox(sid, "title", _emu_in(1), _emu_in(2.3),
                               SLIDE_W - 2 * _emu_in(1), _emu_in(2.4),
                               title_p, anchor="ctr")); sid += 1
        if spec.get("subtitle"):
            sub = "".join(_para(_run(line, 18, color="BBD0E8"), align="ctr",
                                space_after=200)
                          for line in spec["subtitle"].split("\n"))
            shapes.append(_textbox(sid, "subtitle", _emu_in(1), _emu_in(4.7),
                                   SLIDE_W - 2 * _emu_in(1), _emu_in(2.2),
                                   sub, anchor="t")); sid += 1
    else:
        # top accent band + title
        shapes.append(_rect(sid, "band", 0, 0, SLIDE_W, _emu_in(1.15), C_PRIMARY)); sid += 1
        title_p = _para(_run(spec["title"], 26, bold=True, color=C_LIGHT),
                        align="l", space_after=0)
        shapes.append(_textbox(sid, "title", _emu_in(0.5), _emu_in(0.22),
                               SLIDE_W - _emu_in(1), _emu_in(0.8),
                               title_p, anchor="ctr")); sid += 1

        body_y = _emu_in(1.45)
        # optional table
        if spec.get("table"):
            t = spec["table"]
            shapes.append(_table(sid, _emu_in(0.6), body_y,
                                 SLIDE_W - _emu_in(1.2),
                                 t["headers"], t["rows"])); sid += 1
            body_y += _emu_in(0.4) + len(t["rows"]) * 320040 + 370840
            body_y = int(body_y)

        # bullets / paragraphs
        if spec.get("bullets"):
            paras = []
            for item in spec["bullets"]:
                if isinstance(item, tuple):
                    text, level = item
                else:
                    text, level = item, 0
                bold = level == 0 and text.endswith(":")
                size = 20 if level == 0 else 17
                paras.append(_para(_run(text, size,
                                        bold=bold, color=C_TEXT),
                                   level=level, bullet=True, size_pt=size,
                                   space_after=500))
            shapes.append(_textbox(sid, "body", _emu_in(0.7), body_y,
                                   SLIDE_W - _emu_in(1.4),
                                   SLIDE_H - body_y - _emu_in(0.6),
                                   "".join(paras), anchor="t")); sid += 1

        if spec.get("note"):
            note_p = _para(_run(spec["note"], 13, italic=True, color=C_ACCENT),
                           align="l", space_after=0)
            shapes.append(_textbox(sid, "note", _emu_in(0.7),
                                   SLIDE_H - _emu_in(0.7),
                                   SLIDE_W - _emu_in(1.4), _emu_in(0.5),
                                   note_p)); sid += 1

    # page number / footer (all slides)
    foot = _para(_run("%d / %d" % (index, total), 11, color="9AA7B5"),
                 align="r", space_after=0)
    shapes.append(_textbox(sid, "pgnum", SLIDE_W - _emu_in(1.4),
                           SLIDE_H - _emu_in(0.45), _emu_in(1.2),
                           _emu_in(0.3), foot)); sid += 1

    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<p:sld xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
        'xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">'
        '<p:cSld><p:spTree>'
        '<p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>'
        '<p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/>'
        '<a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>'
        '%s</p:spTree></p:cSld><p:clrMapOvr><a:overrideClrMapping '
        'bg1="lt1" tx1="dk1" bg2="lt2" tx2="dk2" accent1="accent1" accent2="accent2" '
        'accent3="accent3" accent4="accent4" accent5="accent5" accent6="accent6" '
        'hlink="hlink" folHlink="folHlink"/></p:clrMapOvr></p:sld>'
        % "".join(shapes)
    )


# ---------------------------------------------------------------------------
# static parts (master, layout, theme)
# ---------------------------------------------------------------------------
_THEME = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    '<a:theme xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" name="Office">'
    '<a:themeElements><a:clrScheme name="Office">'
    '<a:dk1><a:sysClr val="windowText" lastClr="000000"/></a:dk1>'
    '<a:lt1><a:sysClr val="window" lastClr="FFFFFF"/></a:lt1>'
    '<a:dk2><a:srgbClr val="1F3864"/></a:dk2><a:lt2><a:srgbClr val="EEECE1"/></a:lt2>'
    '<a:accent1><a:srgbClr val="2E74B5"/></a:accent1>'
    '<a:accent2><a:srgbClr val="C00000"/></a:accent2>'
    '<a:accent3><a:srgbClr val="2E7D32"/></a:accent3>'
    '<a:accent4><a:srgbClr val="FFC000"/></a:accent4>'
    '<a:accent5><a:srgbClr val="4472C4"/></a:accent5>'
    '<a:accent6><a:srgbClr val="70AD47"/></a:accent6>'
    '<a:hlink><a:srgbClr val="0563C1"/></a:hlink>'
    '<a:folHlink><a:srgbClr val="954F72"/></a:folHlink></a:clrScheme>'
    '<a:fontScheme name="Office"><a:majorFont><a:latin typeface="Calibri"/>'
    '<a:ea typeface=""/><a:cs typeface=""/></a:majorFont>'
    '<a:minorFont><a:latin typeface="Calibri"/><a:ea typeface=""/><a:cs typeface=""/></a:minorFont>'
    '</a:fontScheme><a:fmtScheme name="Office">'
    '<a:fillStyleLst><a:solidFill><a:schemeClr val="phClr"/></a:solidFill>'
    '<a:solidFill><a:schemeClr val="phClr"/></a:solidFill>'
    '<a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:fillStyleLst>'
    '<a:lnStyleLst><a:ln w="6350"><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:ln>'
    '<a:ln w="12700"><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:ln>'
    '<a:ln w="19050"><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:ln></a:lnStyleLst>'
    '<a:effectStyleLst><a:effectStyle><a:effectLst/></a:effectStyle>'
    '<a:effectStyle><a:effectLst/></a:effectStyle>'
    '<a:effectStyle><a:effectLst/></a:effectStyle></a:effectStyleLst>'
    '<a:bgFillStyleLst><a:solidFill><a:schemeClr val="phClr"/></a:solidFill>'
    '<a:solidFill><a:schemeClr val="phClr"/></a:solidFill>'
    '<a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:bgFillStyleLst>'
    '</a:fmtScheme></a:themeElements></a:theme>'
)

_SLIDE_LAYOUT = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    '<p:sldLayout xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
    'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
    'xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" '
    'type="blank" preserve="1"><p:cSld name="Blank"><p:spTree>'
    '<p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>'
    '<p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/>'
    '<a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>'
    '</p:spTree></p:cSld><p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:sldLayout>'
)

_SLIDE_MASTER = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    '<p:sldMaster xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
    'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
    'xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"><p:cSld><p:bg>'
    '<p:bgPr><a:solidFill><a:srgbClr val="FFFFFF"/></a:solidFill><a:effectLst/></p:bgPr></p:bg>'
    '<p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>'
    '<p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/>'
    '<a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>'
    '</p:spTree></p:cSld><p:clrMap bg1="lt1" tx1="dk1" bg2="lt2" tx2="dk2" '
    'accent1="accent1" accent2="accent2" accent3="accent3" accent4="accent4" '
    'accent5="accent5" accent6="accent6" hlink="hlink" folHlink="folHlink"/>'
    '<p:sldLayoutIdLst><p:sldLayoutId id="2147483649" r:id="rId1"/></p:sldLayoutIdLst>'
    '<p:txStyles><p:titleStyle/><p:bodyStyle/><p:otherStyle/></p:txStyles></p:sldMaster>'
)


def build_presentation(slides, out_path):
    n = len(slides)
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)

    # presentation.xml with slide id list
    sld_ids = "".join('<p:sldId id="%d" r:id="rId%d"/>' % (256 + i, i + 1)
                      for i in range(n))
    presentation = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<p:presentation xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
        'xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" saveSubsetFonts="1">'
        '<p:sldMasterIdLst><p:sldMasterId id="2147483648" r:id="rId%d"/></p:sldMasterIdLst>'
        '<p:sldIdLst>%s</p:sldIdLst>'
        '<p:sldSz cx="%d" cy="%d" type="screen16x9"/>'
        '<p:notesSz cx="%d" cy="%d"/></p:presentation>'
        % (n + 1, sld_ids, SLIDE_W, SLIDE_H, SLIDE_H, SLIDE_W)
    )

    # presentation rels: slides rId1..rIdN, master rId(n+1), theme rId(n+2)
    pres_rels = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                 '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">']
    for i in range(n):
        pres_rels.append('<Relationship Id="rId%d" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/slide%d.xml"/>'
                         % (i + 1, i + 1))
    pres_rels.append('<Relationship Id="rId%d" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="slideMasters/slideMaster1.xml"/>' % (n + 1))
    pres_rels.append('<Relationship Id="rId%d" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme" Target="theme/theme1.xml"/>' % (n + 2))
    pres_rels.append('</Relationships>')

    # content types
    overrides = "".join(
        '<Override PartName="/ppt/slides/slide%d.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>' % (i + 1)
        for i in range(n))
    content_types = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        '<Override PartName="/ppt/presentation.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"/>'
        '<Override PartName="/ppt/slideMasters/slideMaster1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideMaster+xml"/>'
        '<Override PartName="/ppt/slideLayouts/slideLayout1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideLayout+xml"/>'
        '<Override PartName="/ppt/theme/theme1.xml" ContentType="application/vnd.openxmlformats-officedocument.theme+xml"/>'
        '%s</Types>' % overrides
    )

    root_rels = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="ppt/presentation.xml"/>'
        '</Relationships>'
    )

    master_rels = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/>'
        '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme" Target="../theme/theme1.xml"/>'
        '</Relationships>'
    )
    layout_rels = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="../slideMasters/slideMaster1.xml"/>'
        '</Relationships>'
    )

    def slide_rels():
        return (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/>'
            '</Relationships>'
        )

    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", content_types)
        z.writestr("_rels/.rels", root_rels)
        z.writestr("ppt/presentation.xml", presentation)
        z.writestr("ppt/_rels/presentation.xml.rels", "".join(pres_rels))
        z.writestr("ppt/theme/theme1.xml", _THEME)
        z.writestr("ppt/slideMasters/slideMaster1.xml", _SLIDE_MASTER)
        z.writestr("ppt/slideMasters/_rels/slideMaster1.xml.rels", master_rels)
        z.writestr("ppt/slideLayouts/slideLayout1.xml", _SLIDE_LAYOUT)
        z.writestr("ppt/slideLayouts/_rels/slideLayout1.xml.rels", layout_rels)
        for i, spec in enumerate(slides):
            z.writestr("ppt/slides/slide%d.xml" % (i + 1),
                       _slide_xml(spec, i + 1, n))
            z.writestr("ppt/slides/_rels/slide%d.xml.rels" % (i + 1),
                       slide_rels())
    return out_path


if __name__ == "__main__":
    demo = [
        {"layout": "title", "title": "Demo Deck",
         "subtitle": "PPTX generator self-test"},
        {"title": "A content slide",
         "bullets": ["First point", ("Sub point", 1), "Second point"]},
        {"title": "A table slide",
         "table": {"headers": ["Model", "F1"],
                   "rows": [["SVM", "0.91"], ["KNN", "0.80"]]}},
    ]
    build_presentation(demo, "tools/_selftest.pptx")
    print("wrote tools/_selftest.pptx")
