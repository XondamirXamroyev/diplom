"""
Markdown -> DOCX compiler built on docxgen.py.

Supported Markdown:
  # / ## / ###            headings (Heading1/2/3, used by Word's auto TOC)
  paragraph text          justified body paragraph
  - item                  bullet list (consecutive lines grouped)
  1. item                 numbered list (consecutive lines grouped)
  | a | b |               table (needs a |---|---| separator row)
  blank line              paragraph separator
  **bold**  *italic*      inline emphasis

Custom directives (whole-line):
  [[TITLE]] text                 large centered bold title
  [[CENTER]] text                centered text
  [[CENTER:b]] text              centered bold
  [[CENTER:i]] text              centered italic
  [[CENTER:bi]] text             centered bold+italic
  [[SIZE:NN]] text               centered text at NN pt
  [[CAPTION]] text               centered italic small caption
  [[FIGURE:relpath|Caption]]     embed an image followed by a caption
  [[PAGEBREAK]]                  page break
  [[TOC]]                        table-of-contents field
"""

import os
import re
import docxgen

_BASE_DIR = "."


def _flush_para(buf, blocks):
    if buf:
        text = " ".join(buf).strip()
        if text:
            blocks.append({"type": "p", "text": text})
        buf.clear()


def markdown_to_blocks(md):
    lines = md.split("\n")
    blocks = []
    para = []
    i = 0
    n = len(lines)

    while i < n:
        line = lines[i]
        stripped = line.strip()

        # ---- directives ----
        if stripped.startswith("[["):
            _flush_para(para, blocks)
            # FIGURE is handled separately because its path contains '/'
            fig = re.match(r"\[\[FIGURE:([^\]|]+)(?:\|(.*?))?\]\]", stripped)
            if fig:
                path = fig.group(1).strip()
                caption = (fig.group(2) or "").strip()
                abspath = os.path.normpath(os.path.join(_BASE_DIR, path))
                blocks.append({"type": "image", "path": abspath})
                if caption:
                    blocks.append({"type": "caption", "text": caption})
                i += 1
                continue
            m = re.match(r"\[\[([A-Z]+)(?::([a-zA-Z0-9]+))?\]\]\s?(.*)", stripped)
            if m:
                tag, arg, rest = m.group(1), m.group(2), m.group(3)
                if tag == "TITLE":
                    blocks.append({"type": "title", "text": rest})
                elif tag == "CENTER":
                    flags = arg or ""
                    blocks.append({"type": "center", "text": rest,
                                   "bold": "b" in flags, "italic": "i" in flags})
                elif tag == "SIZE":
                    size = int(arg) * 2 if arg else docxgen.BODY_HALFPT
                    blocks.append({"type": "center", "text": rest, "size": size})
                elif tag == "CAPTION":
                    blocks.append({"type": "caption", "text": rest})
                elif tag == "PAGEBREAK":
                    blocks.append({"type": "pagebreak"})
                elif tag == "TOC":
                    blocks.append({"type": "toc"})
            i += 1
            continue

        # ---- headings ----
        if stripped.startswith("### "):
            _flush_para(para, blocks)
            blocks.append({"type": "h3", "text": stripped[4:].strip()})
            i += 1
            continue
        if stripped.startswith("## "):
            _flush_para(para, blocks)
            blocks.append({"type": "h2", "text": stripped[3:].strip()})
            i += 1
            continue
        if stripped.startswith("# "):
            _flush_para(para, blocks)
            blocks.append({"type": "h1", "text": stripped[2:].strip()})
            i += 1
            continue

        # ---- table ----
        if stripped.startswith("|") and "|" in stripped[1:]:
            _flush_para(para, blocks)
            tbl = []
            while i < n and lines[i].strip().startswith("|"):
                tbl.append(lines[i].strip())
                i += 1
            rows = []
            for r in tbl:
                cells = [c.strip() for c in r.strip().strip("|").split("|")]
                # skip separator row |---|---|
                if all(re.fullmatch(r":?-{2,}:?", c) for c in cells if c):
                    continue
                rows.append(cells)
            if rows:
                blocks.append({"type": "table", "rows": rows, "header": True})
            continue

        # ---- bullet list ----
        if re.match(r"^[-*]\s+", stripped):
            _flush_para(para, blocks)
            items = []
            while i < n and re.match(r"^[-*]\s+", lines[i].strip()):
                items.append(re.sub(r"^[-*]\s+", "", lines[i].strip()))
                i += 1
            blocks.append({"type": "bullet", "items": items})
            continue

        # ---- numbered list ----
        if re.match(r"^\d+\.\s+", stripped):
            _flush_para(para, blocks)
            items = []
            while i < n and re.match(r"^\d+\.\s+", lines[i].strip()):
                items.append(re.sub(r"^\d+\.\s+", "", lines[i].strip()))
                i += 1
            blocks.append({"type": "num", "items": items})
            continue

        # ---- blank line ----
        if stripped == "":
            _flush_para(para, blocks)
            i += 1
            continue

        # ---- normal paragraph text ----
        para.append(stripped)
        i += 1

    _flush_para(para, blocks)
    return blocks


def build_from_markdown(md_path, out_path):
    global _BASE_DIR
    _BASE_DIR = os.path.dirname(os.path.abspath(md_path))
    with open(md_path, "r", encoding="utf-8") as f:
        md = f.read()
    blocks = markdown_to_blocks(md)
    docxgen.build_document(blocks, out_path)
    return out_path, len(blocks)


if __name__ == "__main__":
    import sys
    src, dst = sys.argv[1], sys.argv[2]
    _, nb = build_from_markdown(src, dst)
    print("wrote %s (%d blocks)" % (dst, nb))
